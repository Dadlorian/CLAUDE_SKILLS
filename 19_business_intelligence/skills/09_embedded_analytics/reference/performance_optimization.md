# Performance Optimization for Embedded Analytics

## Overview

Strategies to optimize embedded analytics for fast load times, responsive interactions, and scalable performance.

## Performance Metrics

### Key Metrics to Track

```javascript
// Performance monitoring
class EmbedPerformanceMonitor {
  trackMetrics() {
    return {
      // Load performance
      timeToFirstByte: this.measureTTFB(),
      domContentLoaded: this.measureDCL(),
      embedLoadTime: this.measureEmbedLoad(),
      dataFetchTime: this.measureDataFetch(),

      // Runtime performance
      queryExecutionTime: this.measureQueryTime(),
      renderTime: this.measureRenderTime(),
      interactionLatency: this.measureInteractionLatency(),

      // Resource usage
      memoryUsage: this.measureMemoryUsage(),
      bundleSize: this.measureBundleSize(),
      networkRequests: this.measureNetworkRequests(),

      // User experience
      largestContentfulPaint: this.measureLCP(),
      firstInputDelay: this.measureFID(),
      cumulativeLayoutShift: this.measureCLS()
    };
  }

  measureEmbedLoad() {
    const start = performance.now();

    return new Promise((resolve) => {
      embedAPI.on('loaded', () => {
        const duration = performance.now() - start;
        this.logMetric('embed_load_time', duration);
        resolve(duration);
      });
    });
  }

  measureQueryTime() {
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.name.includes('analytics-query')) {
          this.logMetric('query_execution_time', entry.duration);
        }
      }
    });

    observer.observe({ entryTypes: ['measure'] });
  }
}

// Performance budgets
const performanceBudgets = {
  embedLoadTime: 2000,      // 2 seconds
  queryExecutionTime: 5000, // 5 seconds
  renderTime: 1000,         // 1 second
  bundleSize: 500000,       // 500 KB
  lcp: 2500,                // 2.5 seconds
  fid: 100,                 // 100ms
  cls: 0.1                  // 0.1 score
};
```

---

## Data Layer Optimization

### 1. Query Optimization

```sql
-- Inefficient query
SELECT *
FROM sales s
JOIN customers c ON s.customer_id = c.id
WHERE s.tenant_id = 123
  AND s.date >= '2024-01-01'
ORDER BY s.date DESC;

-- Optimized query
SELECT
  s.id,
  s.date,
  s.amount,
  c.name
FROM sales s
INNER JOIN customers c
  ON s.customer_id = c.id
  AND s.tenant_id = c.tenant_id
WHERE s.tenant_id = 123
  AND s.date >= '2024-01-01'
  AND s.date < '2024-12-31'
ORDER BY s.date DESC
LIMIT 1000;

-- Add covering index
CREATE INDEX idx_sales_optimized
  ON sales(tenant_id, date DESC)
  INCLUDE (customer_id, amount);

-- Analyze query plan
EXPLAIN (ANALYZE, BUFFERS)
SELECT ...;
```

### 2. Materialized Views and Pre-Aggregation

```sql
-- Create materialized view for common aggregations
CREATE MATERIALIZED VIEW sales_daily_summary AS
SELECT
  tenant_id,
  date,
  COUNT(*) AS transaction_count,
  SUM(amount) AS total_amount,
  AVG(amount) AS avg_amount,
  MAX(amount) AS max_amount,
  MIN(amount) AS min_amount
FROM sales
GROUP BY tenant_id, date;

-- Create index on materialized view
CREATE INDEX idx_sales_daily_summary
  ON sales_daily_summary(tenant_id, date DESC);

-- Refresh strategy
-- Option 1: Scheduled refresh
CREATE OR REPLACE FUNCTION refresh_sales_summary()
RETURNS void AS $$
BEGIN
  REFRESH MATERIALIZED VIEW CONCURRENTLY sales_daily_summary;
END;
$$ LANGUAGE plpgsql;

-- Schedule with pg_cron
SELECT cron.schedule('refresh-sales-summary', '0 */6 * * *', 'SELECT refresh_sales_summary()');

-- Option 2: Incremental refresh
CREATE MATERIALIZED VIEW sales_daily_summary_incremental AS
SELECT * FROM sales_daily_summary;

-- Update only changed rows
REFRESH MATERIALIZED VIEW sales_daily_summary_incremental
WHERE date >= CURRENT_DATE - INTERVAL '7 days';
```

### 3. Extracts and Data Snapshots

```javascript
// Create Tableau extract for performance
class TableauExtractManager {
  async createExtract(tenantId) {
    const extractDef = {
      dataSource: {
        name: `Tenant ${tenantId} Extract`,
        connectionType: 'postgres',
        extractConfig: {
          type: 'hyper',
          refreshSchedule: 'daily',
          incrementalRefresh: {
            enabled: true,
            column: 'updated_at'
          }
        }
      },
      tables: [
        {
          name: 'sales',
          sql: `
            SELECT * FROM sales
            WHERE tenant_id = ${tenantId}
              AND date >= CURRENT_DATE - INTERVAL '2 years'
          `
        }
      ],
      aggregations: [
        {
          name: 'sales_daily',
          dimensions: ['date', 'product_id'],
          measures: {
            total_amount: 'SUM(amount)',
            transaction_count: 'COUNT(*)',
            avg_amount: 'AVG(amount)'
          }
        }
      ]
    };

    await tableau.createExtract(extractDef);
  }

  async scheduleExtractRefresh(tenantId) {
    // Incremental refresh - only new data
    await tableau.scheduleRefresh({
      dataSourceId: `tenant_${tenantId}_extract`,
      schedule: {
        frequency: 'daily',
        time: '02:00',
        timezone: 'UTC'
      },
      incrementalRefresh: true,
      fullRefreshInterval: 'weekly'
    });
  }
}
```

### 4. Query Result Caching

```javascript
class QueryCacheManager {
  constructor() {
    this.redis = new Redis();
    this.defaultTTL = 300; // 5 minutes
  }

  getCacheKey(tenantId, query, params) {
    const queryHash = crypto
      .createHash('md5')
      .update(JSON.stringify({ query, params }))
      .digest('hex');

    return `query_cache:${tenantId}:${queryHash}`;
  }

  async get(tenantId, query, params) {
    const key = this.getCacheKey(tenantId, query, params);
    const cached = await this.redis.get(key);

    if (cached) {
      const data = JSON.parse(cached);
      console.log('Cache hit:', key);
      return { data, cached: true };
    }

    console.log('Cache miss:', key);
    return null;
  }

  async set(tenantId, query, params, data, ttl = this.defaultTTL) {
    const key = this.getCacheKey(tenantId, query, params);

    await this.redis.setex(
      key,
      ttl,
      JSON.stringify(data)
    );

    console.log('Cached:', key, 'TTL:', ttl);
  }

  async invalidate(tenantId, pattern = '*') {
    const keys = await this.redis.keys(`query_cache:${tenantId}:${pattern}`);

    if (keys.length > 0) {
      await this.redis.del(...keys);
      console.log('Invalidated', keys.length, 'cache entries');
    }
  }

  // Adaptive TTL based on query cost
  calculateTTL(queryExecutionTime, dataFreshness) {
    if (dataFreshness === 'real-time') {
      return 30; // 30 seconds
    } else if (dataFreshness === 'near-real-time') {
      return 300; // 5 minutes
    } else if (queryExecutionTime > 10000) {
      // Expensive queries cached longer
      return 3600; // 1 hour
    } else {
      return 600; // 10 minutes (default)
    }
  }
}

// Usage
const cache = new QueryCacheManager();

async function executeQuery(tenantId, query, params) {
  // Try cache first
  const cached = await cache.get(tenantId, query, params);
  if (cached) {
    return cached.data;
  }

  // Execute query
  const start = Date.now();
  const result = await db.query(query, params);
  const executionTime = Date.now() - start;

  // Cache result
  const ttl = cache.calculateTTL(executionTime, 'near-real-time');
  await cache.set(tenantId, query, params, result.rows, ttl);

  return result.rows;
}
```

---

## Frontend Optimization

### 1. Lazy Loading Dashboards

```javascript
// Lazy load analytics on interaction
class LazyAnalyticsLoader {
  constructor() {
    this.loaded = new Set();
  }

  async loadOnVisible(dashboardId, container) {
    // Use Intersection Observer
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(async (entry) => {
          if (entry.isIntersecting && !this.loaded.has(dashboardId)) {
            console.log('Dashboard visible, loading...');
            await this.loadDashboard(dashboardId, container);
            this.loaded.add(dashboardId);
            observer.disconnect();
          }
        });
      },
      {
        rootMargin: '100px' // Load 100px before visible
      }
    );

    observer.observe(container);
  }

  async loadOnClick(dashboardId, button, container) {
    button.addEventListener('click', async () => {
      if (!this.loaded.has(dashboardId)) {
        button.disabled = true;
        button.textContent = 'Loading...';

        await this.loadDashboard(dashboardId, container);

        this.loaded.add(dashboardId);
        button.style.display = 'none';
      }
    }, { once: true });
  }

  async loadDashboard(dashboardId, container) {
    // Show loading state
    container.innerHTML = '<div class="loading">Loading analytics...</div>';

    // Fetch token
    const token = await this.fetchToken();

    // Load SDK if not already loaded
    if (!window.tableau) {
      await this.loadScript('https://tableau.example.com/javascripts/api/tableau-2.9.0.min.js');
    }

    // Embed dashboard
    const viz = new tableau.Viz(container, dashboardUrl, {
      width: '100%',
      height: '800px',
      hideTabs: true,
      onFirstInteractive: () => {
        console.log('Dashboard loaded');
      }
    });
  }

  loadScript(src) {
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = src;
      script.onload = resolve;
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }
}

// Usage
const loader = new LazyAnalyticsLoader();

// Load when visible
const dashboardContainer = document.getElementById('dashboard');
loader.loadOnVisible('sales-dashboard', dashboardContainer);

// Or load on click
const loadButton = document.getElementById('load-analytics');
loader.loadOnClick('sales-dashboard', loadButton, dashboardContainer);
```

### 2. Code Splitting and Dynamic Imports

```javascript
// Split analytics code from main bundle
// main.js - always loaded
import React from 'react';
import { BrowserRouter, Route } from 'react-router-dom';

// analytics.js - loaded on demand
const AnalyticsDashboard = React.lazy(() => import('./AnalyticsDashboard'));

function App() {
  return (
    <BrowserRouter>
      <Route path="/" element={<Home />} />
      <Route
        path="/analytics"
        element={
          <React.Suspense fallback={<div>Loading analytics...</div>}>
            <AnalyticsDashboard />
          </React.Suspense>
        }
      />
    </BrowserRouter>
  );
}

// AnalyticsDashboard.js - separate chunk
export default function AnalyticsDashboard() {
  const [embedSDK, setEmbedSDK] = React.useState(null);

  React.useEffect(() => {
    // Load SDK dynamically
    import('@tableau/embedding-react').then((sdk) => {
      setEmbedSDK(sdk);
    });
  }, []);

  if (!embedSDK) return <div>Loading SDK...</div>;

  return <embedSDK.TableauEmbed src={dashboardUrl} />;
}
```

### 3. Optimized Embedding Configuration

```javascript
// Minimize initial load
const optimizedEmbedConfig = {
  // Defer heavy features
  hideTabs: true,
  hideToolbar: true,

  // Reduce initial data load
  ':refresh': 'no',
  ':render': 'false',

  // Load only what's visible
  ':showVizHome': 'no',
  ':display_count': 'no',

  // Callbacks for progressive enhancement
  onFirstInteractive: async (viz) => {
    console.log('Initial load complete');

    // Lazy load filters
    await viz.showFilters();

    // Lazy load toolbar
    await viz.showToolbar();
  },

  // Optimize for mobile
  device: isMobile() ? 'phone' : 'desktop'
};

function isMobile() {
  return window.innerWidth < 768;
}
```

### 4. Resource Hints and Preloading

```html
<!-- In HTML head -->
<!-- DNS Prefetch for BI platform -->
<link rel="dns-prefetch" href="https://tableau.example.com">
<link rel="dns-prefetch" href="https://app.powerbi.com">

<!-- Preconnect to BI platform -->
<link rel="preconnect" href="https://tableau.example.com">
<link rel="preconnect" href="https://tableau.example.com" crossorigin>

<!-- Preload critical SDK -->
<link
  rel="preload"
  href="https://tableau.example.com/javascripts/api/tableau.min.js"
  as="script"
>

<!-- Prefetch embed token endpoint -->
<link rel="prefetch" href="/api/embed-token">
```

```javascript
// Programmatic prefetching
async function prefetchEmbedToken() {
  // Start fetching token before user navigates to analytics
  const tokenPromise = fetch('/api/embed-token', {
    credentials: 'include'
  });

  // Store promise for later use
  window.__embedTokenPromise = tokenPromise;
}

// Call on app load or user hover
document.getElementById('analytics-link').addEventListener('mouseenter', () => {
  prefetchEmbedToken();
});

// Use prefetched token
async function loadDashboard() {
  const response = await (window.__embedTokenPromise || fetch('/api/embed-token'));
  const { token } = await response.json();

  embedDashboard(token);
}
```

---

## Network Optimization

### 1. CDN for Static Assets

```javascript
// Configure CDN for BI assets
const cdnConfig = {
  tableau: {
    sdk: 'https://cdn.example.com/tableau/tableau-2.9.0.min.js',
    images: 'https://cdn.example.com/tableau/images/',
    fonts: 'https://cdn.example.com/tableau/fonts/'
  },
  powerbi: {
    sdk: 'https://cdn.example.com/powerbi/powerbi.min.js',
    visualizations: 'https://cdn.example.com/powerbi/visuals/'
  }
};

// Load from CDN with fallback
async function loadSDKFromCDN(platform) {
  const cdnUrl = cdnConfig[platform].sdk;
  const fallbackUrl = platformUrls[platform].sdk;

  try {
    await loadScript(cdnUrl);
  } catch (error) {
    console.warn('CDN failed, using fallback');
    await loadScript(fallbackUrl);
  }
}
```

### 2. Compression and Minification

```javascript
// Server-side compression
const compression = require('compression');

app.use(compression({
  level: 6, // Compression level
  threshold: 1024, // Only compress > 1KB
  filter: (req, res) => {
    // Compress analytics responses
    if (req.path.startsWith('/api/analytics')) {
      return true;
    }
    return compression.filter(req, res);
  }
}));

// Brotli compression for static assets
app.get('/assets/*', (req, res) => {
  const acceptsEncoding = req.headers['accept-encoding'];

  if (acceptsEncoding && acceptsEncoding.includes('br')) {
    res.setHeader('Content-Encoding', 'br');
    res.sendFile(req.path + '.br');
  } else if (acceptsEncoding && acceptsEncoding.includes('gzip')) {
    res.setHeader('Content-Encoding', 'gzip');
    res.sendFile(req.path + '.gz');
  } else {
    res.sendFile(req.path);
  }
});
```

### 3. HTTP/2 Server Push

```javascript
// Push critical resources
app.get('/analytics', (req, res) => {
  // Push SDK
  res.push('/static/tableau-sdk.js', {
    response: {
      'content-type': 'application/javascript'
    }
  });

  // Push embed token
  res.push('/api/embed-token', {
    request: {
      method: 'POST'
    }
  });

  res.render('analytics');
});
```

---

## Database Optimization

### 1. Connection Pooling

```javascript
const { Pool } = require('pg');

// Optimized connection pool
const pool = new Pool({
  host: 'postgres.example.com',
  database: 'analytics',
  user: 'app_user',
  password: process.env.DB_PASSWORD,

  // Pool configuration
  max: 20,                    // Max connections
  idleTimeoutMillis: 30000,   // Close idle after 30s
  connectionTimeoutMillis: 2000, // Timeout connecting

  // Statement timeout
  statement_timeout: 30000,   // 30 seconds max query time

  // Performance options
  application_name: 'analytics_app',
  keepAlive: true,
  keepAliveInitialDelayMillis: 10000
});

// Monitor pool health
pool.on('error', (err) => {
  console.error('Unexpected pool error', err);
});

pool.on('connect', () => {
  console.log('New database connection');
});

// Pool stats
setInterval(() => {
  console.log('Pool stats:', {
    total: pool.totalCount,
    idle: pool.idleCount,
    waiting: pool.waitingCount
  });
}, 60000);
```

### 2. Read Replicas for Analytics

```javascript
class DatabaseRouter {
  constructor() {
    // Write pool (primary)
    this.writePool = new Pool({ ...primaryConfig });

    // Read pools (replicas)
    this.readPools = [
      new Pool({ ...replica1Config }),
      new Pool({ ...replica2Config }),
      new Pool({ ...replica3Config })
    ];

    this.currentReadIndex = 0;
  }

  // Route writes to primary
  async executeWrite(query, params) {
    return this.writePool.query(query, params);
  }

  // Route reads to replicas (round-robin)
  async executeRead(query, params) {
    const pool = this.readPools[this.currentReadIndex];
    this.currentReadIndex = (this.currentReadIndex + 1) % this.readPools.length;

    return pool.query(query, params);
  }

  // Analytics queries always go to replicas
  async executeAnalyticsQuery(query, params) {
    // Pick least loaded replica
    const pool = await this.getLeastLoadedReplica();
    return pool.query(query, params);
  }

  async getLeastLoadedReplica() {
    const loads = await Promise.all(
      this.readPools.map(async (pool) => ({
        pool,
        load: pool.totalCount - pool.idleCount
      }))
    );

    loads.sort((a, b) => a.load - b.load);
    return loads[0].pool;
  }
}

const db = new DatabaseRouter();

// Usage
app.get('/api/analytics/sales', async (req, res) => {
  // Automatically routed to read replica
  const result = await db.executeAnalyticsQuery(
    'SELECT * FROM sales WHERE tenant_id = $1',
    [req.user.tenantId]
  );

  res.json(result.rows);
});
```

### 3. Query Optimization Techniques

```sql
-- Partition large tables by date
CREATE TABLE sales_partitioned (
  id SERIAL,
  tenant_id INTEGER NOT NULL,
  date DATE NOT NULL,
  amount DECIMAL(10,2)
) PARTITION BY RANGE (date);

-- Create partitions
CREATE TABLE sales_2024_q1 PARTITION OF sales_partitioned
  FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');

CREATE TABLE sales_2024_q2 PARTITION OF sales_partitioned
  FOR VALUES FROM ('2024-04-01') TO ('2024-07-01');

-- Queries automatically use partition pruning
EXPLAIN SELECT * FROM sales_partitioned
WHERE date >= '2024-01-01' AND date < '2024-02-01';
-- Only scans sales_2024_q1 partition

-- Composite index for common query patterns
CREATE INDEX idx_sales_composite
  ON sales(tenant_id, date DESC, product_id)
  WHERE status = 'completed';

-- Partial index for active data only
CREATE INDEX idx_sales_active
  ON sales(tenant_id, date)
  WHERE archived = false;

-- Expression index for computed columns
CREATE INDEX idx_sales_month
  ON sales(tenant_id, DATE_TRUNC('month', date));
```

---

## Monitoring and Profiling

### Performance Monitoring Dashboard

```javascript
class PerformanceMonitor {
  async collectRealTimeMetrics() {
    return {
      // Database performance
      database: {
        activeConnections: await this.getActiveConnections(),
        avgQueryTime: await this.getAvgQueryTime(),
        slowQueries: await this.getSlowQueries(),
        cacheHitRate: await this.getCacheHitRate()
      },

      // Application performance
      application: {
        requestsPerSecond: await this.getRequestRate(),
        avgResponseTime: await this.getAvgResponseTime(),
        errorRate: await this.getErrorRate(),
        memoryUsage: process.memoryUsage()
      },

      // BI platform performance
      biPlatform: {
        embedLoadTime: await this.getAvgEmbedLoadTime(),
        queryExecutionTime: await this.getAvgBIQueryTime(),
        concurrentUsers: await this.getConcurrentUsers(),
        dashboardViews: await this.getDashboardViews()
      },

      // Cache performance
      cache: {
        hitRate: await this.getCacheHitRate(),
        missRate: await this.getCacheMissRate(),
        evictionRate: await this.getCacheEvictionRate(),
        size: await this.getCacheSize()
      }
    };
  }

  async detectPerformanceIssues() {
    const metrics = await this.collectRealTimeMetrics();

    const issues = [];

    // Detect slow queries
    if (metrics.database.avgQueryTime > 5000) {
      issues.push({
        type: 'slow_queries',
        severity: 'high',
        message: `Avg query time ${metrics.database.avgQueryTime}ms exceeds threshold`
      });
    }

    // Detect cache issues
    if (metrics.cache.hitRate < 0.7) {
      issues.push({
        type: 'low_cache_hit_rate',
        severity: 'medium',
        message: `Cache hit rate ${metrics.cache.hitRate} below 70%`
      });
    }

    // Detect connection pool saturation
    if (metrics.database.activeConnections > 18) {
      issues.push({
        type: 'connection_pool_saturation',
        severity: 'high',
        message: 'Connection pool near capacity'
      });
    }

    return issues;
  }
}
```

---

## Performance Checklist

### Data Layer
- [ ] Queries optimized with proper indexes
- [ ] Materialized views for common aggregations
- [ ] Query result caching implemented
- [ ] Connection pooling configured
- [ ] Read replicas for analytics queries
- [ ] Table partitioning for large datasets
- [ ] Regular VACUUM and ANALYZE

### Frontend
- [ ] Lazy loading for analytics components
- [ ] Code splitting for BI SDKs
- [ ] Resource hints and preloading
- [ ] Optimized embed configuration
- [ ] Progressive enhancement strategy
- [ ] Bundle size under budget
- [ ] Core Web Vitals within targets

### Network
- [ ] CDN for static assets
- [ ] Compression enabled (gzip/brotli)
- [ ] HTTP/2 or HTTP/3
- [ ] DNS prefetch and preconnect
- [ ] Minimize API calls
- [ ] Request batching where possible

### Caching
- [ ] Multi-layer caching strategy
- [ ] Adaptive TTL based on query cost
- [ ] Cache invalidation strategy
- [ ] Cache warming for common queries
- [ ] Monitor cache hit rates

### Monitoring
- [ ] Real-time performance monitoring
- [ ] Slow query logging and alerting
- [ ] User-perceived performance tracking
- [ ] Regular performance audits
- [ ] Capacity planning reviews
