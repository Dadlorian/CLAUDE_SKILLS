# CDN Cache Invalidation Guide

## Cache Invalidation Strategies

### Strategy 1: TTL-Based (Time Expiration)

**How It Works:**
```
Content cached with TTL (Time-To-Live)
After TTL seconds, cache expires
Next request fetches from origin

Example:
Cache-Control: max-age=3600
TTL = 3600 seconds (1 hour)

Query at 10:00 AM: Cached
Query at 10:30 AM: Cached (still fresh)
Query at 11:00 AM: Expired, fetches from origin
```

**Best For:**
- Non-critical content that changes infrequently
- Content with predictable update frequency
- High traffic (avoids invalidation overhead)

**Configuration:**
```hcl
# Cloudflare
resource "cloudflare_cache_rules" "example" {
  zone_id = var.zone_id

  rules {
    description = "Cache HTML 1 hour"
    if           = "http.request.uri.path matches \"/.*\\.html$\""
    then = {
      cache     = true
      cache_ttl = 3600
    }
  }

  rules {
    description = "Cache CSS/JS 1 year"
    if           = "http.request.uri.path matches \"/static/.*\""
    then = {
      cache     = true
      cache_ttl = 31536000
    }
  }
}

# AWS CloudFront
resource "aws_cloudfront_distribution" "example" {
  default_cache_behavior {
    default_ttl = 3600
    max_ttl     = 86400
  }
}
```

**Pros:**
- Simple, automatic
- No API calls needed
- Predictable cache behavior

**Cons:**
- Stale content served for up to TTL seconds
- No immediate update capability
- Fixed expiration (can't adapt to content changes)

### Strategy 2: Event-Based Purging (Manual Invalidation)

**How It Works:**
```
Content updated in source
Manual API call purges cache
Cache immediately empty
Next request fetches fresh

Example:
Blog post published
→ Call cache purge API
→ Next user gets fresh post (not stale)
```

**Best For:**
- Critical content updates
- Time-sensitive information
- Content with frequent unpredictable changes

**Cloudflare API Purge:**
```bash
# Purge by URL
curl -X POST "https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  --data '{"files": ["https://example.com/blog/post-1.html"]}'

# Purge multiple URLs
curl -X POST "https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  --data '{
    "files": [
      "https://example.com/blog/post-1.html",
      "https://example.com/blog/post-2.html",
      "https://example.com/blog/index.html"
    ]
  }'

# Purge by tag
curl -X POST "https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  --data '{"tags": ["blog", "featured"]}'

# Purge entire cache
curl -X POST "https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  --data '{"purge_everything": true}'
```

**AWS CloudFront Invalidation:**
```bash
# Create invalidation
aws cloudfront create-invalidation \
  --distribution-id E123ABC \
  --paths "/blog/post-1.html" "/blog/post-2.html"

# Invalidate wildcard paths
aws cloudfront create-invalidation \
  --distribution-id E123ABC \
  --paths "/blog/*" "/images/*"

# Terraform
resource "aws_cloudfront_invalidation" "example" {
  distribution_id = aws_cloudfront_distribution.example.id
  paths           = ["/blog/*", "/images/*"]
}
```

**Fastly Cache Purge:**
```bash
# Soft purge (serve stale, fetch fresh background)
curl -X POST "https://api.fastly.com/purge" \
  -H "Fastly-Key: {api_key}" \
  --data "example.com/blog/post-1.html"

# Hard purge (immediate cache clear)
curl -X POST "https://api.fastly.com/purge" \
  -H "Fastly-Key: {api_key}" \
  --data "example.com/blog/post-1.html"
```

**Pros:**
- Immediate cache clearing
- Precise control over what to invalidate
- Good for critical updates

**Cons:**
- Increased origin traffic (cache misses)
- API calls required
- Risk of cache stampede

### Strategy 3: Hybrid (TTL + Event Purge)

**How It Works:**
```
Set long TTL for efficiency
Soft purge on content update (serve stale, fetch fresh)
Client gets stale immediately
Background fetch fresh content

Example:
Cache-Control: max-age=86400, stale-while-revalidate=604800
TTL = 1 day
Stale-while-revalidate = 7 days

Blog post updated at 2 PM:
- Soft purge triggers
- Users at 2:01 PM: See stale version (returned immediately)
- Users at 2:02 PM: See fresh version (background fetch complete)
- Avoids cache stampede
- Eventually consistent
```

**Best For:**
- High-traffic content
- Acceptable eventual consistency
- Balance between freshness and performance

**Soft Purge Implementation:**
```bash
# Cloudflare soft purge
curl -X POST "https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  --data '{
    "files": ["https://example.com/blog/post-1.html"],
    "purge_everything": false
  }'

# Fastly soft purge
curl -X POST "https://api.fastly.com/purge/example.com/blog/post-1.html" \
  -H "Fastly-Key: {api_key}" \
  -H "Soft-Purge: 1"  # Soft purge flag

# HTTP Cache header
Cache-Control: public, max-age=3600, stale-while-revalidate=86400
```

**Pros:**
- Balance of freshness and performance
- No cache stampede
- Immediate response to users
- Efficient origin protection

**Cons:**
- Initial users see stale content
- Requires stale-while-revalidate support

### Strategy 4: Cache Key-Based (Content Versioning)

**How It Works:**
```
Content versioned with hash or version number
Each version has unique URL
Old version cached, new version fetched
No purge needed

Example:
app.abc123.js (version 1) -> cached forever
app.xyz789.js (version 2) -> new URL, not cached

Users fetch new URL automatically
```

**Best For:**
- Static assets (CSS, JS, images)
- Immutable content
- High-traffic content

**Implementation:**
```javascript
// Webpack generates hash-based filenames
output: {
  filename: 'js/[name].[contenthash].js',
  assetModuleFilename: 'assets/[name].[contenthash][ext]'
}

// HTML
<script src="/js/app.abc123def456.js"></script>

// On update
<script src="/js/app.xyz789abc012.js"></script>

// Old version still cached (different URL)
// New version fetched immediately
// No cache invalidation needed!
```

**Cache Settings:**
```hcl
# CloudFront
default_cache_behavior {
  # Static assets: cache forever
  cache_ttl = 31536000  # 1 year
  max_ttl   = 31536000

  # Browser: don't revalidate
  viewer_protocol_policy = "https-only"
}
```

**Pros:**
- No cache invalidation needed
- Maximum cache efficiency
- Instant version switching

**Cons:**
- Requires versioning infrastructure
- Old versions accumulate (clean up periodically)
- Not suitable for dynamic content

## Cache Invalidation Patterns

### Pattern 1: Tag-Based Invalidation

**Concept:**
```
Related content tagged together
One API call purges entire group

Example:
Blog post:
  - /blog/post-123.html [tag: post-123]
  - /author/john.html [tag: author-john]
  - /category/tech.html [tag: category-tech]
  - /blog/ [tag: homepage]

When post updates, purge tag: post-123
All related pages purged
```

**Implementation:**
```bash
# Set cache tag on responses
Cloudflare API:
X-Cache-Tag: post-123, author-john, category-tech

# Purge all tagged content
curl -X POST "https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache" \
  -H "Authorization: Bearer {token}" \
  --data '{"tags": ["post-123"]}'
```

**Terraform:**
```hcl
resource "cloudflare_cache_rules" "tag_cache" {
  zone_id = var.zone_id

  rules {
    description = "Cache blog posts with tag"
    if           = "http.request.uri.path matches \"/blog/.*\""
    then = {
      cache        = true
      cache_tags   = "blog,article"
      cache_ttl    = 3600
    }
  }
}
```

### Pattern 2: Dependency-Based Invalidation

**Concept:**
```
Track content dependencies
Invalidate dependent content when source updates

Example:
Product price changes
→ Invalidate:
  - /products/item-123.html
  - /checkout/cart.html
  - /user/recommendations.html
  - /admin/inventory.html
```

**Implementation:**
```python
# Python example
class CacheInvalidator:
    def __init__(self, cdn_client):
        self.cdn = cdn_client

    def invalidate_on_event(self, event_type, item_id):
        """Invalidate related content based on event"""

        invalidation_map = {
            "product_updated": [
                f"/products/item-{item_id}.html",
                "/products/",
                "/recommendations/",
            ],
            "blog_post_published": [
                f"/blog/post-{item_id}.html",
                "/blog/",
                f"/author/{author_id}/",
                f"/category/{category_id}/",
            ],
            "user_profile_updated": [
                f"/profile/{item_id}/",
                "/recommendations/",
            ]
        }

        paths_to_purge = invalidation_map.get(event_type, [])
        self.cdn.purge_urls(paths_to_purge)

# Usage
invalidator = CacheInvalidator(cloudflare_client)
invalidator.invalidate_on_event("product_updated", "item-123")
```

### Pattern 3: Time-Based Scheduled Invalidation

**Concept:**
```
Invalidate at specific times
Useful for news, weather, time-sensitive content

Example:
Invalidate homepage every 5 minutes
Invalidate weather every 30 seconds
Invalidate news feed every minute
```

**Implementation:**
```python
# Scheduled invalidation with APScheduler
from apscheduler.schedulers.background import BackgroundScheduler
import cloudflare_client

scheduler = BackgroundScheduler()

# Invalidate homepage every 5 minutes
scheduler.add_job(
    func=cloudflare_client.purge_urls,
    args=[["https://example.com/"]],
    trigger="interval",
    minutes=5,
    id="homepage_purge"
)

# Invalidate weather every 30 seconds
scheduler.add_job(
    func=cloudflare_client.purge_urls,
    args=[["https://example.com/weather/"]],
    trigger="interval",
    seconds=30,
    id="weather_purge"
)

scheduler.start()
```

## Monitoring and Cost

### Cache Invalidation Metrics

```
Track:
1. Purges per day
2. URLs invalidated
3. Cache hit ratio after purge
4. Time to populate cache

Target:
- < 100 purges/day (excessive purging indicates TTL too low)
- CHR recovery < 10 minutes after purge
- CHR > 85% overall
```

### Cost Considerations

**Cloudflare:**
```
Soft purges: Free
Hard purges: Free (included)
Full zone purges: Free (up to 30/day)

Cost: Free tier through Enterprise
```

**AWS CloudFront:**
```
Invalidations: $0.005 per invalidation path
Limit: 3000 paths per month free
Additional: $0.005 per path

Example:
100 invalidations × 1 path = $0.50/month
100 invalidations × 10 paths = $5.00/month
```

**Fastly:**
```
Purges: Included
No per-purge cost

Only pay for traffic served
```

## Best Practices

1. **Use Long TTLs**: Minimize purges
2. **Cache Versioning**: For static assets, use content hash
3. **Tag-Based Purging**: Group related content
4. **Monitoring**: Track purge frequency and CHR
5. **Soft Purging**: Prefer soft over hard purges
6. **Dependencies**: Map content relationships
7. **Testing**: Test invalidation strategy before production
8. **Documentation**: Document purge logic and schedules
9. **Gradual**: Purge selectively, not entire cache
10. **Automation**: Automate purge API calls from CMS

## Troubleshooting

### Issue: Cache Not Invalidating

```
Check:
1. API credentials correct
2. URL format matches cached URL
3. Zone ID correct
4. API rate limits not exceeded

Test:
curl -X POST "https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache" \
  -H "Authorization: Bearer {token}" \
  --data '{"files": ["https://example.com/test.html"]}'

Response should be: {"success": true}
```

### Issue: Cache Miss Storm After Purge

```
Solution (Stale-While-Revalidate):
Cache-Control: max-age=3600, stale-while-revalidate=86400

CDN returns stale content immediately
Fetches fresh in background
Avoids origin overload
```

### Issue: Excessive Purge Costs

```
Optimization:
1. Increase TTL
2. Use cache tags (fewer API calls)
3. Implement soft purges
4. Schedule purges (batch them)

Before:
100 individual purges = $0.50

After:
10 tag-based purges = $0.05
```
