# Caching Strategies for Embedded Analytics

## Overview

Multi-layer caching strategies to optimize embedded analytics performance, reduce database load, and improve user experience.

## Caching Layers

```
┌─────────────────────────────────────────┐
│    Browser Cache (Client-Side)         │
├─────────────────────────────────────────┤
│    CDN Cache (Edge)                     │
├─────────────────────────────────────────┤
│    Application Cache (Redis/Memcached) │
├─────────────────────────────────────────┤
│    Query Result Cache                   │
├─────────────────────────────────────────┤
│    Materialized Views                   │
├─────────────────────────────────────────┤
│    Database Query Cache                 │
└─────────────────────────────────────────┘
```

---

## Layer 1: Browser Caching

### HTTP Cache Headers

```javascript
// Set cache headers for static BI assets
app.get('/static/tableau-sdk.js', (req, res) => {
  res.set({
    'Cache-Control': 'public, max-age=31536000, immutable',
    'ETag': generateETag(fileContent),
    'Last-Modified': new Date(fileStat.mtime).toUTCString()
  });

  res.sendFile(filePath);
});

// Cache embed tokens briefly (client-side)
app.post('/api/embed-token', async (req, res) => {
  const token = await generateEmbedToken(req.user);

  res.set({
    'Cache-Control': 'private, max-age=300', // 5 minutes
    'Vary': 'Cookie' // Cache per user
  });

  res.json({ token });
});

// Don't cache user-specific analytics data
app.get('/api/analytics/data', async (req, res) => {
  const data = await fetchAnalyticsData(req.user);

  res.set({
    'Cache-Control': 'private, no-cache, no-store, must-revalidate',
    'Pragma': 'no-cache',
    'Expires': '0'
  });

  res.json(data);
});
```

### Service Worker Caching

```javascript
// service-worker.js
const CACHE_NAME = 'analytics-v1';
const STATIC_ASSETS = [
  '/static/tableau-sdk.js',
  '/static/powerbi-sdk.js',
  '/static/styles.css',
  '/static/logo.png'
];

// Install service worker and cache static assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(STATIC_ASSETS))
  );
});

// Serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Return cached response if available
        if (response) {
          return response;
        }

        // Clone request for network
        const fetchRequest = event.request.clone();

        return fetch(fetchRequest).then((response) => {
          // Don't cache non-successful responses
          if (!response || response.status !== 200) {
            return response;
          }

          // Cache static assets only
          if (event.request.url.includes('/static/')) {
            const responseToCache = response.clone();

            caches.open(CACHE_NAME)
              .then((cache) => {
                cache.put(event.request, responseToCache);
              });
          }

          return response;
        });
      })
  );
});
```

### LocalStorage Token Caching

```javascript
class TokenCacheManager {
  constructor() {
    this.storageKey = 'analytics_token';
  }

  getCachedToken() {
    const cached = localStorage.getItem(this.storageKey);

    if (!cached) return null;

    const { token, expiresAt } = JSON.parse(cached);

    // Check if expired (with 1 minute buffer)
    if (Date.now() > expiresAt - 60000) {
      localStorage.removeItem(this.storageKey);
      return null;
    }

    return token;
  }

  cacheToken(token, expiresIn) {
    const expiresAt = Date.now() + (expiresIn * 1000);

    localStorage.setItem(this.storageKey, JSON.stringify({
      token,
      expiresAt
    }));
  }

  clearCache() {
    localStorage.removeItem(this.storageKey);
  }
}

// Usage
async function getEmbedToken() {
  const cache = new TokenCacheManager();

  // Try cache first
  const cachedToken = cache.getCachedToken();
  if (cachedToken) {
    return cachedToken;
  }

  // Fetch new token
  const response = await fetch('/api/embed-token', {
    method: 'POST',
    credentials: 'include'
  });

  const { token, expiresIn } = await response.json();

  // Cache for next time
  cache.cacheToken(token, expiresIn);

  return token;
}
```

---

## Layer 2: CDN Caching

### CloudFlare Configuration

```javascript
// Set cache headers for CDN
app.use('/cdn-assets/*', (req, res, next) => {
  // CloudFlare cache everything for 1 year
  res.set({
    'Cache-Control': 'public, max-age=31536000',
    'CDN-Cache-Control': 'max-age=31536000',
    'Cloudflare-CDN-Cache-Control': 'max-age=31536000'
  });

  next();
});

// Purge CDN cache when assets update
async function purgeCDNCache(urls) {
  await axios.post('https://api.cloudflare.com/client/v4/zones/ZONE_ID/purge_cache', {
    files: urls
  }, {
    headers: {
      'Authorization': `Bearer ${process.env.CLOUDFLARE_API_TOKEN}`,
      'Content-Type': 'application/json'
    }
  });
}

// Usage: purge when deploying new BI SDK version
await purgeCDNCache([
  'https://cdn.example.com/static/tableau-sdk.js',
  'https://cdn.example.com/static/powerbi-sdk.js'
]);
```

### AWS CloudFront Configuration

```javascript
const AWS = require('aws-sdk');
const cloudfront = new AWS.CloudFront();

async function invalidateCloudFrontCache(paths) {
  const params = {
    DistributionId: process.env.CLOUDFRONT_DISTRIBUTION_ID,
    InvalidationBatch: {
      CallerReference: Date.now().toString(),
      Paths: {
        Quantity: paths.length,
        Items: paths
      }
    }
  };

  const result = await cloudfront.createInvalidation(params).promise();
  console.log('Cache invalidated:', result.Invalidation.Id);
}

// Usage
await invalidateCloudFrontCache([
  '/static/*',
  '/dashboards/sales.json'
]);
```

---

## Layer 3: Application-Level Caching (Redis)

### Query Result Caching

```javascript
const Redis = require('ioredis');
const redis = new Redis({
  host: 'redis.example.com',
  port: 6379,
  password: process.env.REDIS_PASSWORD,
  db: 0,
  keyPrefix: 'analytics:',
  retryStrategy: (times) => {
    return Math.min(times * 50, 2000);
  }
});

class QueryCache {
  constructor(redis) {
    this.redis = redis;
  }

  getCacheKey(tenantId, query, params) {
    const queryHash = crypto
      .createHash('sha256')
      .update(JSON.stringify({ query, params }))
      .digest('hex');

    return `query:${tenantId}:${queryHash}`;
  }

  async get(tenantId, query, params) {
    const key = this.getCacheKey(tenantId, query, params);

    try {
      const cached = await this.redis.get(key);

      if (cached) {
        const data = JSON.parse(cached);

        // Update access time for LRU
        await this.redis.expire(key, this.getTTL(tenantId));

        return {
          data: data.result,
          cached: true,
          cachedAt: data.timestamp
        };
      }

      return null;
    } catch (error) {
      console.error('Cache get error:', error);
      return null; // Fail open
    }
  }

  async set(tenantId, query, params, result, customTTL = null) {
    const key = this.getCacheKey(tenantId, query, params);
    const ttl = customTTL || this.getTTL(tenantId);

    const cacheData = {
      result,
      timestamp: Date.now(),
      query: query.substring(0, 100), // Store partial query for debugging
      tenantId
    };

    try {
      await this.redis.setex(
        key,
        ttl,
        JSON.stringify(cacheData)
      );

      // Track cache stats
      await this.trackCacheStats(tenantId, 'set');
    } catch (error) {
      console.error('Cache set error:', error);
      // Don't throw - caching failure shouldn't break request
    }
  }

  async invalidate(tenantId, pattern = '*') {
    const searchPattern = `query:${tenantId}:${pattern}`;
    const stream = this.redis.scanStream({
      match: searchPattern,
      count: 100
    });

    let deleted = 0;

    stream.on('data', async (keys) => {
      if (keys.length) {
        const pipeline = this.redis.pipeline();
        keys.forEach((key) => {
          // Remove key prefix before deleting
          pipeline.del(key.replace('analytics:', ''));
        });
        await pipeline.exec();
        deleted += keys.length;
      }
    });

    return new Promise((resolve) => {
      stream.on('end', () => {
        console.log(`Invalidated ${deleted} cache entries for tenant ${tenantId}`);
        resolve(deleted);
      });
    });
  }

  getTTL(tenantId) {
    // Different TTL based on tenant tier
    const tierTTLs = {
      enterprise: 3600,    // 1 hour
      professional: 1800,  // 30 minutes
      basic: 600           // 10 minutes
    };

    const tenant = this.getTenantTier(tenantId);
    return tierTTLs[tenant] || 600;
  }

  async trackCacheStats(tenantId, operation) {
    const statsKey = `stats:${tenantId}:${operation}`;
    await this.redis.incr(statsKey);
    await this.redis.expire(statsKey, 86400); // 24 hours
  }

  async getCacheStats(tenantId) {
    const hits = await this.redis.get(`stats:${tenantId}:hit`) || 0;
    const misses = await this.redis.get(`stats:${tenantId}:miss`) || 0;
    const sets = await this.redis.get(`stats:${tenantId}:set`) || 0;

    const total = parseInt(hits) + parseInt(misses);
    const hitRate = total > 0 ? (parseInt(hits) / total) : 0;

    return {
      hits: parseInt(hits),
      misses: parseInt(misses),
      sets: parseInt(sets),
      hitRate: hitRate.toFixed(2),
      total
    };
  }
}

// Usage
const queryCache = new QueryCache(redis);

async function executeQuery(tenantId, query, params) {
  // Try cache
  const cached = await queryCache.get(tenantId, query, params);

  if (cached) {
    console.log('Cache hit');
    await queryCache.trackCacheStats(tenantId, 'hit');
    return cached.data;
  }

  console.log('Cache miss');
  await queryCache.trackCacheStats(tenantId, 'miss');

  // Execute query
  const result = await db.query(query, params);

  // Cache result
  await queryCache.set(tenantId, query, params, result.rows);

  return result.rows;
}
```

### Token Caching

```javascript
class TokenCache {
  constructor(redis) {
    this.redis = redis;
  }

  async getToken(userId, dashboardId) {
    const key = `token:${userId}:${dashboardId}`;
    const token = await this.redis.get(key);

    if (token) {
      return JSON.parse(token);
    }

    return null;
  }

  async setToken(userId, dashboardId, token, expiresIn) {
    const key = `token:${userId}:${dashboardId}`;

    // Cache for slightly less than actual expiry
    const cacheTTL = expiresIn - 60; // 1 minute buffer

    await this.redis.setex(
      key,
      cacheTTL,
      JSON.stringify(token)
    );
  }

  async revokeToken(userId, dashboardId = null) {
    if (dashboardId) {
      await this.redis.del(`token:${userId}:${dashboardId}`);
    } else {
      // Revoke all tokens for user
      const pattern = `token:${userId}:*`;
      const keys = await this.redis.keys(pattern);

      if (keys.length > 0) {
        await this.redis.del(...keys);
      }
    }
  }
}
```

### Dashboard Metadata Caching

```javascript
class DashboardCache {
  constructor(redis) {
    this.redis = redis;
  }

  async getDashboard(dashboardId) {
    const key = `dashboard:${dashboardId}`;
    const cached = await this.redis.get(key);

    if (cached) {
      return JSON.parse(cached);
    }

    return null;
  }

  async setDashboard(dashboardId, metadata) {
    const key = `dashboard:${dashboardId}`;

    // Cache dashboard metadata for 1 hour
    await this.redis.setex(
      key,
      3600,
      JSON.stringify(metadata)
    );
  }

  async invalidateDashboard(dashboardId) {
    await this.redis.del(`dashboard:${dashboardId}`);
  }

  // Warm cache with popular dashboards
  async warmCache(tenantId) {
    const popularDashboards = await db.query(`
      SELECT dashboard_id, COUNT(*) as views
      FROM analytics_views
      WHERE tenant_id = $1
        AND viewed_at > NOW() - INTERVAL '7 days'
      GROUP BY dashboard_id
      ORDER BY views DESC
      LIMIT 10
    `, [tenantId]);

    for (const { dashboard_id } of popularDashboards.rows) {
      const metadata = await this.fetchDashboardMetadata(dashboard_id);
      await this.setDashboard(dashboard_id, metadata);
    }

    console.log(`Warmed cache with ${popularDashboards.rows.length} dashboards`);
  }
}
```

---

## Layer 4: BI Platform Caching

### Tableau Extract Caching

```javascript
// Create and cache Tableau extracts
class TableauExtractCache {
  async createExtract(tenantId, dataSourceId) {
    // Create Tableau extract (Hyper file)
    const extract = await tableau.createExtract({
      dataSourceId,
      type: 'hyper',
      includeAll: true
    });

    // Schedule incremental refresh
    await tableau.scheduleRefresh({
      extractId: extract.id,
      schedule: {
        frequency: 'hourly',
        incrementalRefresh: true
      }
    });

    return extract;
  }

  async warmExtractCache(tenantId) {
    // Trigger extract refresh to warm cache
    await tableau.refreshExtract({
      tenantId,
      wait: false // Async refresh
    });
  }
}
```

### Power BI Dataset Refresh

```javascript
// Cache Power BI datasets with refresh
class PowerBIDatasetCache {
  async refreshDataset(datasetId) {
    // Trigger dataset refresh
    await powerbi.refreshDataset({
      datasetId,
      notifyOption: 'NoNotification'
    });
  }

  async scheduleRefresh(datasetId, schedule) {
    await powerbi.updateRefreshSchedule({
      datasetId,
      schedule: {
        days: schedule.days || ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
        times: schedule.times || ['06:00', '12:00', '18:00'],
        enabled: true,
        localTimeZoneId: 'UTC'
      }
    });
  }
}
```

---

## Adaptive Caching Strategies

### Time-Based TTL

```javascript
class AdaptiveCacheManager {
  calculateTTL(queryMetrics) {
    const {
      executionTime,
      resultSize,
      queryComplexity,
      dataStaleness,
      tenantTier
    } = queryMetrics;

    let ttl = 300; // Base 5 minutes

    // Increase TTL for slow queries
    if (executionTime > 10000) {
      ttl = 3600; // 1 hour for very slow queries
    } else if (executionTime > 5000) {
      ttl = 1800; // 30 minutes for slow queries
    }

    // Decrease TTL for real-time requirements
    if (dataStaleness === 'real-time') {
      ttl = Math.min(ttl, 60); // Max 1 minute
    } else if (dataStaleness === 'near-real-time') {
      ttl = Math.min(ttl, 300); // Max 5 minutes
    }

    // Adjust for tenant tier
    const tierMultipliers = {
      basic: 0.5,       // Shorter cache for basic
      professional: 1,  // Standard cache
      enterprise: 2     // Longer cache for enterprise
    };

    ttl *= tierMultipliers[tenantTier] || 1;

    // Increase TTL for large result sets (expensive to recompute)
    if (resultSize > 100000) {
      ttl *= 1.5;
    }

    return Math.min(ttl, 7200); // Cap at 2 hours
  }

  shouldCache(queryMetrics) {
    const {
      executionTime,
      resultSize,
      cacheHitRate
    } = queryMetrics;

    // Don't cache fast queries with low hit rate
    if (executionTime < 100 && cacheHitRate < 0.1) {
      return false;
    }

    // Always cache slow queries
    if (executionTime > 5000) {
      return true;
    }

    // Don't cache very large results
    if (resultSize > 10000000) { // 10MB
      return false;
    }

    // Cache if hit rate suggests benefit
    return cacheHitRate > 0.2;
  }
}
```

### Cache Warming

```javascript
class CacheWarmer {
  constructor(queryCache, db) {
    this.queryCache = queryCache;
    this.db = db;
  }

  async warmPopularQueries(tenantId) {
    // Find most executed queries
    const popularQueries = await this.db.query(`
      SELECT
        query,
        params,
        COUNT(*) as execution_count
      FROM query_log
      WHERE tenant_id = $1
        AND executed_at > NOW() - INTERVAL '24 hours'
      GROUP BY query, params
      ORDER BY execution_count DESC
      LIMIT 20
    `, [tenantId]);

    console.log(`Warming cache with ${popularQueries.rows.length} queries`);

    for (const { query, params } of popularQueries.rows) {
      try {
        // Execute and cache
        const result = await this.db.query(query, JSON.parse(params));
        await this.queryCache.set(tenantId, query, JSON.parse(params), result.rows);
      } catch (error) {
        console.error('Error warming query:', error);
      }
    }
  }

  // Schedule cache warming
  scheduleCacheWarming(tenantId) {
    // Warm cache every 6 hours
    setInterval(async () => {
      await this.warmPopularQueries(tenantId);
    }, 6 * 60 * 60 * 1000);

    // Initial warming
    this.warmPopularQueries(tenantId);
  }
}
```

---

## Cache Invalidation

### Event-Based Invalidation

```javascript
class CacheInvalidator {
  constructor(queryCache, redis) {
    this.queryCache = queryCache;
    this.redis = redis;
  }

  async onDataChange(event) {
    const { tenantId, table, operation } = event;

    console.log(`Data changed: ${table} (${operation}) for tenant ${tenantId}`);

    // Invalidate all queries touching this table
    await this.queryCache.invalidate(tenantId, `*${table}*`);

    // Publish invalidation event for distributed systems
    await this.redis.publish('cache:invalidate', JSON.stringify({
      tenantId,
      table,
      operation,
      timestamp: Date.now()
    }));
  }

  // Listen for data changes
  setupChangeListeners() {
    // PostgreSQL LISTEN/NOTIFY
    const pgClient = new Client();
    await pgClient.connect();

    await pgClient.query('LISTEN data_changes');

    pgClient.on('notification', (msg) => {
      const event = JSON.parse(msg.payload);
      this.onDataChange(event);
    });
  }

  // Trigger from application
  async notifyDataChange(tenantId, table, operation) {
    await db.query(
      "SELECT pg_notify('data_changes', $1)",
      [JSON.stringify({ tenantId, table, operation })]
    );
  }
}

// Usage: invalidate cache when data changes
app.post('/api/sales', async (req, res) => {
  const sale = await db.sales.insert({
    tenant_id: req.user.tenantId,
    amount: req.body.amount,
    date: req.body.date
  });

  // Notify cache invalidation
  await cacheInvalidator.notifyDataChange(
    req.user.tenantId,
    'sales',
    'insert'
  );

  res.json(sale);
});
```

### Time-Based Invalidation

```javascript
// Scheduled cache invalidation
const cron = require('node-cron');

// Clear cache for non-enterprise tenants every hour
cron.schedule('0 * * * *', async () => {
  const tenants = await db.query(`
    SELECT id FROM tenants
    WHERE tier != 'enterprise'
  `);

  for (const { id } of tenants.rows) {
    await queryCache.invalidate(id);
  }

  console.log('Hourly cache invalidation complete');
});

// Clear all cache at midnight
cron.schedule('0 0 * * *', async () => {
  await redis.flushdb();
  console.log('Daily cache flush complete');
});
```

---

## Monitoring Cache Performance

```javascript
class CacheMonitor {
  async getMetrics() {
    const info = await redis.info('stats');

    return {
      // Redis stats
      keyspaceHits: this.parseInfo(info, 'keyspace_hits'),
      keyspaceMisses: this.parseInfo(info, 'keyspace_misses'),
      hitRate: this.calculateHitRate(info),

      // Memory usage
      usedMemory: this.parseInfo(info, 'used_memory'),
      usedMemoryPeak: this.parseInfo(info, 'used_memory_peak'),
      memFragRatio: this.parseInfo(info, 'mem_fragmentation_ratio'),

      // Eviction
      evictedKeys: this.parseInfo(info, 'evicted_keys'),

      // Connections
      connectedClients: this.parseInfo(info, 'connected_clients'),
      blockedClients: this.parseInfo(info, 'blocked_clients')
    };
  }

  calculateHitRate(info) {
    const hits = this.parseInfo(info, 'keyspace_hits');
    const misses = this.parseInfo(info, 'keyspace_misses');
    const total = hits + misses;

    return total > 0 ? (hits / total).toFixed(2) : 0;
  }

  async detectIssues() {
    const metrics = await this.getMetrics();
    const issues = [];

    if (metrics.hitRate < 0.7) {
      issues.push({
        type: 'low_hit_rate',
        severity: 'medium',
        message: `Cache hit rate ${metrics.hitRate} below 70%`,
        recommendation: 'Increase TTL or warm cache more aggressively'
      });
    }

    if (metrics.memFragRatio > 1.5) {
      issues.push({
        type: 'memory_fragmentation',
        severity: 'low',
        message: `Memory fragmentation ratio ${metrics.memFragRatio}`,
        recommendation: 'Consider Redis restart during maintenance window'
      });
    }

    if (metrics.evictedKeys > 1000) {
      issues.push({
        type: 'high_eviction',
        severity: 'high',
        message: `${metrics.evictedKeys} keys evicted`,
        recommendation: 'Increase Redis memory or reduce TTL'
      });
    }

    return issues;
  }
}
```

---

## Cache Best Practices Checklist

- [ ] Implement multi-layer caching strategy
- [ ] Set appropriate TTLs based on data staleness
- [ ] Use cache keys that include tenant context
- [ ] Monitor cache hit rates (target > 70%)
- [ ] Implement cache invalidation on data changes
- [ ] Use Redis or equivalent for application cache
- [ ] Enable CDN for static assets
- [ ] Configure browser caching with proper headers
- [ ] Warm cache with popular queries
- [ ] Set cache size limits to prevent OOM
- [ ] Monitor cache memory usage
- [ ] Implement adaptive caching based on query cost
- [ ] Test cache invalidation in staging
- [ ] Document caching strategy for team
- [ ] Regular cache performance reviews
