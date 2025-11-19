# Performance Tuning Guide

## Database Optimization

### 1. Add Indexes

```sql
-- Compound index for common queries
CREATE INDEX idx_sales_tenant_date
  ON sales(tenant_id, date DESC);

-- Covering index (avoid table lookups)
CREATE INDEX idx_sales_covering
  ON sales(tenant_id, date)
  INCLUDE (amount, customer_id);

-- Verify index usage
EXPLAIN ANALYZE
SELECT * FROM sales
WHERE tenant_id = 123 AND date >= '2024-01-01';
```

### 2. Materialized Views

```sql
CREATE MATERIALIZED VIEW sales_daily AS
SELECT
  tenant_id,
  DATE(created_at) as date,
  SUM(amount) as total_amount,
  COUNT(*) as transaction_count
FROM sales
GROUP BY tenant_id, DATE(created_at);

-- Refresh nightly
REFRESH MATERIALIZED VIEW CONCURRENTLY sales_daily;
```

### 3. Connection Pooling

```javascript
const pool = new Pool({
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
  statement_timeout: 30000
});
```

## Application Caching

### Query Result Cache

```javascript
const cache = new QueryCache(redis);

async function getData(tenantId, query) {
  const cached = await cache.get(tenantId, query);
  if (cached) return cached;

  const result = await db.query(query);
  await cache.set(tenantId, query, result, 300); // 5 min TTL

  return result;
}
```

### Token Cache

```javascript
const tokenCache = new Map();

async function getToken(userId) {
  if (tokenCache.has(userId)) {
    const { token, expiresAt } = tokenCache.get(userId);
    if (Date.now() < expiresAt) return token;
  }

  const token = await generateToken(userId);
  tokenCache.set(userId, {
    token,
    expiresAt: Date.now() + (25 * 60 * 1000) // 25 min
  });

  return token;
}
```

## Frontend Optimization

### Lazy Loading

```javascript
const AnalyticsDashboard = React.lazy(() => 
  import('./AnalyticsDashboard')
);

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <AnalyticsDashboard />
    </Suspense>
  );
}
```

### Code Splitting

```javascript
// webpack.config.js
module.exports = {
  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        tableau: {
          test: /tableau/,
          name: 'tableau-sdk'
        },
        powerbi: {
          test: /powerbi/,
          name: 'powerbi-sdk'
        }
      }
    }
  }
};
```

## Monitoring

```javascript
class PerformanceMonitor {
  async collectMetrics() {
    return {
      avgQueryTime: await this.getAvgQueryTime(),
      cacheHitRate: await this.getCacheHitRate(),
      embedLoadTime: await this.getEmbedLoadTime()
    };
  }

  async detectSlowQueries() {
    const slowQueries = await db.query(`
      SELECT query, avg_duration
      FROM query_log
      WHERE avg_duration > 5000
      GROUP BY query
      ORDER BY avg_duration DESC
      LIMIT 10
    `);

    for (const q of slowQueries.rows) {
      console.warn('Slow query:', q.query, q.avg_duration, 'ms');
    }
  }
}
```

## Performance Checklist

- [ ] Database indexes optimized
- [ ] Query result caching enabled
- [ ] Connection pooling configured
- [ ] Lazy loading implemented
- [ ] Bundle size < 500KB
- [ ] CDN for static assets
- [ ] Compression enabled
- [ ] Embed load time < 3s
- [ ] Query time < 5s
- [ ] Cache hit rate > 70%
