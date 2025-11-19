# CDN Cache Strategies

## Cache Hit Ratio Optimization

### Measurement
```
Cache Hit Ratio (CHR) = (Cache Hits / Total Requests) * 100

Example:
- Hits: 9500
- Misses: 500
- CHR: (9500 / 10000) * 100 = 95%

Good CHR targets:
- Static content: 95%+ (images, CSS, JS)
- API responses: 60-80% (depends on content freshness)
- HTML pages: 70-85% (depends on update frequency)
- Overall: 85%+ for typical website
```

### Monitoring CHR
```
Cloudflare metrics:
- Cache hit ratio in dashboard
- Breakdown by content type
- Trends over time

CloudWatch custom metrics:
aws cloudwatch put-metric-data --namespace "CDN" \
  --metric-name "CacheHitRatio" \
  --value 95.5

Splunk query:
index=cdn sourcetype=cdn_log
| stats sum(eval(cache_status="HIT")) as hits, count as total
| eval chr = round((hits/total)*100, 2)
```

### Improving Cache Hit Ratio

#### 1. Extend TTL
```
Before:
Cache-Control: max-age=300 (5 minutes)
CHR: 75%

After:
Cache-Control: max-age=3600 (1 hour)
CHR: 88%

Trade-offs:
- Longer TTL = higher CHR
- Longer TTL = slower updates
- Balance: TTL = update frequency / 2
```

#### 2. Remove Query Strings
```
Before:
/product.html?utm_source=google&utm_medium=cpc
/product.html?utm_source=facebook&utm_medium=social
= 2 separate cache entries

After (remove tracking params):
/product.html
= 1 cache entry (100% hit rate)

Implementation:
- Ignore query string in cache key
- Track analytics separately
- Reduce parameter bloat

CDN configuration:
URL query string handling = ignore
Cache key = scheme + host + path (ignore query)
```

#### 3. Normalize Cookies
```
Before:
Cookie: session=abc123def456
Cookie: session=xyz789abc123
= Different cache entries per user

After (cookie normalization):
Extract only essential cookies
- Session ID: Keep
- Analytics: Remove
- Tracking: Remove

Implementation:
Cache key = base URL + only session_id

Result:
Multiple users share same cached response
CHR increases significantly
```

#### 4. Use Cache Tags
```
Related content grouped by tag:
/blog/post-123 -> Cache-Tag: post-123, blog, featured
/author/john -> Cache-Tag: author-john, blog
/category/tech -> Cache-Tag: category-tech, blog

When post updates:
Purge all tagged content in 1 operation
Faster than individual URL purges

Example:
1 blog post update affects:
- /blog/post-123 (post)
- /author/john (author page)
- /category/tech (category page)
- /blog/ (homepage)

Single cache tag purge: post-123
```

## Caching Dynamic Content

### API Response Caching
```
Typical API response:
GET /api/users/123

Options:
1. Don't cache (TTL=0)
   - Always fresh
   - High origin load
   - User sees delays

2. Cache short duration (TTL=60)
   - 60 seconds fresh
   - 60% CHR (requests within window)
   - Good balance

3. Cache with validation (TTL=3600, stale-while-revalidate=86400)
   - Serve cached for 1 hour
   - Revalidate in background for 1 day
   - Always fast response
   - Eventually consistent

Configuration:
Cache-Control: public, max-age=60, stale-while-revalidate=86400
ETag: "abc123def456"
```

### Database Query Caching
```
Pattern 1: Cache DB query results
Request -> CDN -> Origin -> Database
                       |
                   Cache Result

TTL: Query-dependent
- User list: 5 minutes (changes infrequently)
- Activity feed: 30 seconds (changes frequently)
- Inventory: 10 seconds (real-time needs)

Implementation:
db_cache_key = query_string + parameter_hash
ttl = 300  # for user list
```

### Conditional Caching
```
Cache by user role:
- Anonymous: Cache for 3600 seconds
- Logged-in: Cache for 60 seconds
- Admin: No caching (always fresh)

Implementation:
if user_role == "anonymous":
  cache_ttl = 3600
elif user_role == "logged_in":
  cache_ttl = 60
else:
  cache_ttl = 0

CDN configuration:
Cache-Control header varies by Cookie: role=admin
```

## Cache Busting Strategies

### Version-Based Busting
```
Static asset versioning:

Old approach (cache busting issue):
<script src="/js/app.js"></script>
-> If app.js updates, browser needs TTL to expire (might cache old version)

New approach (fingerprinting):
<script src="/js/app.abc123def456.js"></script>
-> Build process creates unique filename per version
-> Old version and new version coexist in cache
-> Switch instantly by updating HTML

Build configuration:
webpack config:
output: {
  filename: 'js/[name].[contenthash].js'
}

Result:
- app.abc123def456.js (old version)
- app.xyz789abc012.js (new version)
- HTML updated to point to new version
- Both cached, instant switch
```

### Query String Versioning
```
Old approach:
<script src="/js/app.js?v=1.0.0"></script>

After update:
<script src="/js/app.js?v=1.0.1"></script>

Cache behavior:
- Different query string = different cache entry
- Old version cached at /js/app.js?v=1.0.0
- New version cached at /js/app.js?v=1.0.1

Downside:
- Query strings clutter URLs
- Analytics may split traffic

Recommendation:
Use fingerprinting (hash) instead
```

### Service Worker Cache Busting
```
Service Worker controls client cache:

// On update, skip waiting
self.addEventListener('install', event => {
  self.skipWaiting();  // Activate immediately
});

// Clear old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames
          .filter(name => name !== CACHE_VERSION)
          .map(name => caches.delete(name))
      );
    })
  );
});

CACHE_VERSION = 'v1.2.3'  // Update per release
```

## Partial Caching

### Cache Partial Responses
```
Full page: 100 KB
Cacheable section: 80 KB (static header/footer)
Dynamic section: 20 KB (personalized content)

Caching strategy:
1. Cache static parts (header, footer, sidebar)
2. Fetch dynamic part from origin
3. Assemble on edge or client

ESI (Edge Side Includes):
<html>
  <esi:include src="/static/header.html" ttl="86400" />
  <div id="dynamic">
    <!-- Fetched from origin every request -->
    <esi:include src="/dynamic/user-feed.html" ttl="0" />
  </div>
  <esi:include src="/static/footer.html" ttl="86400" />
</html>

Cloudflare example:
resource "cloudflare_page_rule" "cache_esi" {
  zone_id = var.zone_id
  target  = "example.com/*"

  actions {
    cache_on_cookie = "session"
    cache_level     = "cache_everything"
    esi             = "on"
  }
}
```

## Cache Warming

### Proactive Cache Warming
```
Scenario:
Site deployed at 9 AM
First user query = cache miss = 500ms response
Second user query = cache hit = 50ms response

Solution: Warm cache before users arrive

Implementation:
1. Deploy at 8:50 AM
2. Run cache warming script at 8:55 AM
3. Script crawls important pages
4. Pages cached at edge
5. First real user gets cache hit

Script example:
urls_to_warm = [
  "/",
  "/products/",
  "/about/",
  "/contact/",
]

for url in urls_to_warm:
  request GET https://example.com + url
  # Primes cache at edge
```

### Intelligent Prefetch
```
Client-side prefetch:
<link rel="prefetch" href="/next-page.html">

Predictive prefetch:
- Analyze user navigation patterns
- Prefetch likely next page
- Download in background
- User clicks -> instant load

Implementation:
// After user hovers over link for 1 second
document.querySelectorAll('a').forEach(link => {
  link.addEventListener('mouseenter', () => {
    setTimeout(() => {
      if (link.matches(':hover')) {
        const prefetchLink = document.createElement('link');
        prefetchLink.rel = 'prefetch';
        prefetchLink.href = link.href;
        document.head.appendChild(prefetchLink);
      }
    }, 1000);
  });
});
```

## Cache Invalidation Patterns

### Pattern 1: TTL-Based (Time)
```
Simple time-based invalidation:

Cache-Control: max-age=3600
TTL: 1 hour
Update: Every 1 hour maximum staleness

Best for: Non-critical content, blogs, documentation
```

### Pattern 2: Event-Based (Manual)
```
Invalidate on content update:

CMS publishes content
-> Webhook to cache purge
-> API call: purge /blog/post-123
-> Cache cleared
-> Next request fresh

Best for: Critical content, real-time needs
```

### Pattern 3: Hybrid (TTL + Event)
```
Set long TTL with event purge:

Cache-Control: max-age=86400, stale-while-revalidate=604800
TTL: 1 day
Stale window: 7 days

Content update:
-> Soft purge (mark as stale)
-> User gets stale immediately
-> Background fetch fresh content
-> 7 days later, TTL expires

Best for: Balance freshness + performance
```

### Pattern 4: Dependency-Based
```
Cache invalidation chains:

Update blog post -> Invalidate:
- /blog/post-123
- /blog/
- /feed.xml
- /author/john
- /category/tech

Implementation:
POST /cache-purge
{
  "dependencies": [
    "post-123",
    "blog-homepage",
    "author-john"
  ]
}
```

## Multi-Region Cache Strategy

### Regional Cache Tiers
```
Tier 1: Global CDN Edge (275+ locations)
- Small cache, regional content
- Hit rate: 80-90%

Tier 2: Regional Cache Nodes (30+ regions)
- Larger cache, regional + popular content
- Hit rate: 90-95%

Tier 3: Origin Shield (optional)
- Protected cache between CDN and origin
- Hit rate: 95%+

Request path:
Miss at edge -> Check regional -> Check shield -> Origin

Benefits:
- Multiple caching layers
- Protects origin from traffic spikes
- Faster recovery from edge misses
```

### Geographic Content Routing
```
Route by location:

US traffic -> cdn.us.example.com
  - Cached in USA datacenters
  - Optimized for US users

EU traffic -> cdn.eu.example.com
  - Cached in EU datacenters
  - Optimized for EU users
  - GDPR compliance (data residency)

APAC traffic -> cdn.apac.example.com
  - Cached in Asia-Pacific datacenters

Configuration:
if request.origin_country in ["US", "CA", "MX"]:
  route to cdn.us.example.com
elif request.origin_country in EU_COUNTRIES:
  route to cdn.eu.example.com
else:
  route to cdn.apac.example.com
```

## Cache Metrics & Monitoring

### Key Metrics
```
Cache Hit Ratio = Hits / Total Requests
Cache Bytes Served = Bytes delivered from cache
Origin Load = Bandwidth saved by caching

Example dashboard:
CHR: 92.5%
Cache Bytes: 50 GB / 55 GB (91%)
Origin Protection: 45 GB cached (82% reduction)

Alert thresholds:
CHR < 70% -> Investigate
Origin Load > 100 Mbps -> Scale up origin
Cache Size Growth > 50% -> Review TTLs
```

### Optimization Feedback Loop
```
Measure -> Analyze -> Optimize -> Measure

1. Measure CHR, breakdown by content type
2. Identify low CHR categories
3. Optimize TTLs, cache keys, purging
4. Re-measure to verify improvement
5. Repeat

Monthly optimization:
- Review top cache misses
- Analyze miss reasons
- Implement improvements
- Target: 2-5% CHR improvement per month
```
