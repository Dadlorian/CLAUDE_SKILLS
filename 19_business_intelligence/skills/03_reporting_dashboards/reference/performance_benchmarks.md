# Dashboard Performance Benchmarks

## Why Performance Matters

### User Impact
- **<3 seconds**: Acceptable, users stay engaged
- **3-5 seconds**: Tolerable, user attention wanders
- **5-10 seconds**: Poor, users consider leaving
- **>10 seconds**: Abandoned, productivity destroyed

### Business Impact
- Every 1-second delay = 7% reduction in conversions
- 40% of users abandon after 3 seconds
- Slow dashboards = reduced usage = poor ROI on BI investment

---

## Performance Targets

### Load Time Benchmarks

**Initial Load (Time to Interactive)**
```
Excellent:  < 2 seconds
Good:       2-3 seconds
Acceptable: 3-5 seconds
Poor:       5-10 seconds
Failed:     > 10 seconds
```

**Incremental/Filter Updates**
```
Excellent:  < 500ms
Good:       500ms - 1s
Acceptable: 1s - 2s
Poor:       > 2s
```

**Auto-Refresh**
```
Background: Should not block UI
Acceptable: < 2 seconds per refresh
Frequency:  User-configurable (30s - 5min)
```

### Rendering Benchmarks

**Frame Rate (Animations, Interactions)**
```
Smooth:     60 FPS (16.67ms per frame)
Acceptable: 30 FPS (33.33ms per frame)
Janky:      < 30 FPS (noticeable lag)
```

**Chart Rendering**
```
Simple chart (1 series, <100 points):   < 100ms
Complex chart (3-5 series, 100s points): < 500ms
Very complex (10+ series, 1000s points): < 2s
```

### Data Volume Benchmarks

**Recommended Limits**
```
Table rows (per page):      25-100 rows
Table columns (visible):    5-10 columns
Chart data points (total):  < 5,000 points
Chart series:               < 10 series
Dashboard visuals:          8-15 visuals per page
```

**Maximum Limits (Before Performance Degrades)**
```
Tableau:
- Marks per sheet:    100,000 - 500,000
- Rows from DB:       < 1M (use aggregation)
- Live connection:    < 10M rows recommended

Power BI:
- Rows per table:     100M+ (Import mode)
- DirectQuery:        Query < 30s
- Live connection:    Dependent on source

Looker:
- Query result:       < 5,000 rows recommended
- Row limit:          50,000 (configurable)
```

---

## Performance Optimization Strategies

### 1. Data Layer Optimization

#### Aggregation
**Problem**: Querying million-row tables
**Solution**: Pre-aggregate at database level

```sql
-- ❌ Bad: Query detail table for every dashboard load
SELECT date, product, SUM(revenue)
FROM sales_transactions  -- 10M rows
GROUP BY date, product;

-- ✓ Good: Query pre-aggregated table
SELECT date, product, revenue
FROM sales_daily_summary  -- 10K rows
WHERE date >= CURRENT_DATE - 90;
```

**Benchmarks**:
- Aggregated query: 100-500ms
- Detail query: 5-30 seconds

#### Indexing
**Critical Indexes**:
- Date columns (most common filter)
- Foreign keys
- Commonly filtered dimensions

```sql
CREATE INDEX idx_sales_date ON sales(sale_date);
CREATE INDEX idx_sales_product ON sales(product_id);
CREATE INDEX idx_sales_region ON sales(region_id);
```

**Impact**: 10-100x query speed improvement

#### Materialized Views
```sql
CREATE MATERIALIZED VIEW mv_daily_metrics AS
SELECT
  date_trunc('day', created_at) as date,
  product_category,
  COUNT(*) as order_count,
  SUM(revenue) as total_revenue,
  AVG(revenue) as avg_revenue
FROM orders
GROUP BY 1, 2;

-- Refresh nightly
REFRESH MATERIALIZED VIEW mv_daily_metrics;
```

**Benchmarks**:
- Query materialized view: 10-100ms
- Query base tables: 1-10 seconds

#### Data Extract vs Live Connection

**Extract (Recommended for dashboards)**
```
Pros:
- Fast (data in memory)
- Reduced DB load
- Works offline

Cons:
- Not real-time
- Requires refresh schedule

Benchmark: < 1 second query time
```

**Live Connection**
```
Pros:
- Always current
- No storage needed

Cons:
- Slower queries
- DB load
- Requires connection

Benchmark: 1-10 seconds query time
```

**Hybrid Approach**
```
- Historical data: Extract (refreshed daily)
- Today's data: Live connection
- Combined in dashboard
```

### 2. Query Optimization

#### Limit Result Sets
```sql
-- ❌ Bad: Return all data, filter client-side
SELECT * FROM sales;  -- 10M rows

-- ✓ Good: Filter at database
SELECT *
FROM sales
WHERE date >= '2024-01-01'
  AND region = 'North'
LIMIT 10000;  -- 100 rows
```

#### Avoid Correlated Subqueries
```sql
-- ❌ Bad: Correlated subquery (runs for each row)
SELECT
  p.product_name,
  (SELECT AVG(revenue)
   FROM sales s
   WHERE s.product_id = p.product_id) as avg_rev
FROM products p;

-- ✓ Good: Join
SELECT
  p.product_name,
  AVG(s.revenue) as avg_rev
FROM products p
LEFT JOIN sales s ON p.product_id = s.product_id
GROUP BY p.product_name;
```

#### Use Appropriate Joins
```sql
-- ✓ Good: INNER JOIN (faster, if appropriate)
SELECT a.*, b.name
FROM large_table a
INNER JOIN small_lookup b ON a.id = b.id;

-- Slower: LEFT JOIN (if not needed)
```

#### Optimize Date Filters
```sql
-- ❌ Bad: Function on column prevents index use
SELECT * FROM sales
WHERE YEAR(sale_date) = 2024;

-- ✓ Good: Range query uses index
SELECT * FROM sales
WHERE sale_date >= '2024-01-01'
  AND sale_date < '2025-01-01';
```

### 3. Dashboard Design Optimization

#### Reduce Visual Count
```
❌ 25 charts on one page
   - Slow to render
   - Cognitive overload
   - Many simultaneous queries

✓ 8-12 charts per page
   - Faster rendering
   - Better UX
   - Manageable queries
```

#### Lazy Loading
```javascript
// Load above-fold content first
loadVisibleCharts();

// Load below-fold when scrolled
window.addEventListener('scroll', () => {
  if (isNearBottom()) {
    loadRemainingCharts();
  }
});
```

**Benchmark Impact**: 50-70% faster initial load

#### Progressive Enhancement
```
1. Load skeleton/placeholder (instant)
2. Load summary metrics (< 1s)
3. Load simple charts (< 2s)
4. Load complex charts (< 5s)
5. Load drill-down data (on demand)
```

#### Filter Efficiency

**Cascading Filters** (optimize order):
```
1. Filter by date (reduces 80% of data)
2. Filter by region (reduces another 60%)
3. Filter by product (final refinement)

Result: Query 10K rows instead of 10M
```

**Single Apply vs Auto-Apply**:
```
❌ Auto-apply: Every filter change triggers query
   - User selects 5 filters = 5 queries

✓ Apply button: User selects all filters, then applies
   - 5 filter selections = 1 query
```

### 4. Caching Strategies

#### Client-Side Caching
```javascript
// Cache query results
const cache = new Map();

function getData(query) {
  const key = JSON.stringify(query);

  if (cache.has(key)) {
    return Promise.resolve(cache.get(key)); // Instant
  }

  return fetchData(query).then(data => {
    cache.set(key, data);
    return data;
  });
}
```

**Benchmark**: Cached queries return in <10ms

#### Server-Side Caching
```
Redis cache:
- Cache query results: 1 hour TTL
- Cache aggregations: 24 hour TTL
- Invalidate on data update

Benchmark:
- Cached: 10-50ms
- Uncached: 1-10 seconds
```

#### Dashboard-Level Caching
```
Tableau Server:
- Cache: 1-12 hours
- Preload cache: Scheduled refresh before business hours

Power BI:
- Scheduled refresh: Daily/hourly
- DirectQuery: No caching (always live)
```

### 5. Network Optimization

#### Minimize Payload Size
```
❌ Bad: Return all columns
SELECT * FROM sales;  -- 50 columns, 10MB

✓ Good: Return only needed columns
SELECT date, product, revenue  -- 3 columns, 500KB
FROM sales;
```

**Benchmark**: 20x smaller payload = 20x faster transfer

#### Compression
```
Enable GZIP compression:
- Uncompressed JSON: 10 MB
- GZIP compressed: 1 MB

Transfer time on 10 Mbps connection:
- Uncompressed: 8 seconds
- Compressed: 800ms
```

#### CDN for Static Assets
```
Dashboard framework, chart libraries:
- Without CDN: 2-5 seconds
- With CDN: 200-500ms
```

---

## Platform-Specific Benchmarks

### Tableau

**Performance Recording**
```
Tools > Performance Recording

Targets:
- Computing Layouts: < 1s
- Executing Query:   < 2s
- Rendering:         < 500ms
```

**Optimization Tips**:
```
1. Use extracts instead of live
   Impact: 10-100x faster

2. Aggregate dimensions
   Impact: 50-90% fewer marks

3. Avoid quick filters on high-cardinality fields
   Impact: 2-5s faster initial load

4. Context filters before other filters
   Impact: 50-80% query time reduction

5. Use boolean calculated fields instead of string
   Impact: 20-40% faster
```

### Power BI

**Performance Analyzer**
```
View > Performance Analyzer

Targets:
- DAX query:        < 1s
- Visual display:   < 500ms
- Other:            < 100ms
```

**Optimization Tips**:
```
1. Use Import mode over DirectQuery when possible
   Impact: 10-50x faster

2. Reduce cardinality in data model
   Impact: 50% smaller file, 2x faster

3. Use variables in DAX
   Impact: 30-50% faster complex calculations

4. Avoid bi-directional relationships
   Impact: 2-5x faster query time

5. Use column store over row store
   Impact: 10-20x compression, faster scans
```

### Looker

**Query Performance**
```
Develop > SQL Runner > Explain

Targets:
- Compile LookML:  < 100ms
- Run query:       < 5s (< 30s absolute max)
- Render:          < 1s
```

**Optimization Tips**:
```
1. Use persistent derived tables (PDTs)
   Impact: Query pre-aggregated data, 10-100x faster

2. Use datagroups for caching
   Impact: Cached results instant

3. Aggregate awareness
   Impact: Auto-use aggregated tables

4. Limit rows in explores
   Impact: Prevent accidental massive queries

5. Use symmetric aggregates
   Impact: Enable aggregate awareness
```

---

## Monitoring & Measurement

### Key Metrics to Track

**Dashboard Performance Metrics**:
```
Load Time (p50):        Median load time
Load Time (p95):        95th percentile (worst experiences)
Time to Interactive:    When users can interact
Query Time:             Database query duration
Render Time:            Chart rendering duration
Error Rate:             % of failed loads
Abandonment Rate:       % of users leaving before load
```

### Tools

**Browser Tools**:
```
Chrome DevTools:
- Network tab: Load times, payload sizes
- Performance tab: Rendering performance
- Lighthouse: Overall performance score

Targets:
- Performance score: > 90
- First Contentful Paint: < 1.8s
- Time to Interactive: < 3.5s
- Total Blocking Time: < 200ms
```

**Platform Tools**:
```
Tableau Server:
- Admin Views > Performance
- Background Tasks for Extracts
- Traffic to Views

Power BI:
- Premium metrics app
- Performance Analyzer
- Usage metrics

Looker:
- System Activity > Dashboard Performance
- History (query times)
- Alerts for slow queries
```

**APM Tools**:
```
- New Relic
- Datadog
- AppDynamics

Track:
- Query duration
- API latency
- User sessions
- Error rates
```

---

## Performance Testing

### Load Testing
```
Simulate concurrent users:
- 10 users: Dashboard should perform normally
- 50 users: Acceptable degradation (<20%)
- 100 users: May require optimization
- 500+ users: Enterprise architecture needed

Tools:
- JMeter
- Gatling
- LoadRunner
```

### Stress Testing
```
Test limits:
- Maximum data volume
- Maximum concurrent users
- Maximum refresh rate
- Recovery from failure

Identify breaking points before users do
```

### Regression Testing
```
After changes, verify:
- Load time unchanged or improved
- Query time unchanged or improved
- No new errors introduced

Automate with CI/CD
```

---

## Optimization Checklist

**Data Layer**:
- [ ] Aggregate data at source (not in dashboard)
- [ ] Index commonly filtered columns
- [ ] Use materialized views for complex calculations
- [ ] Limit result sets with WHERE clauses
- [ ] Use extracts instead of live connections (when appropriate)

**Query Layer**:
- [ ] Optimize SQL queries (no correlated subqueries)
- [ ] Use appropriate joins
- [ ] Filter early (reduce rows before processing)
- [ ] Limit columns to only what's needed
- [ ] Add LIMIT clauses to prevent runaway queries

**Dashboard Layer**:
- [ ] Limit to 8-15 visuals per page
- [ ] Use lazy loading for below-fold content
- [ ] Progressive enhancement (critical content first)
- [ ] Single "Apply" button for filters (not auto-apply)
- [ ] Simplify complex visualizations

**Caching**:
- [ ] Enable server-side caching
- [ ] Set appropriate cache TTL
- [ ] Preload cache before business hours
- [ ] Implement client-side caching for static data
- [ ] Cache invalidation strategy defined

**Network**:
- [ ] Minimize payload size (only needed data)
- [ ] Enable compression (GZIP)
- [ ] Use CDN for static assets
- [ ] Optimize images (compress, appropriate format)

**Monitoring**:
- [ ] Track load times (p50, p95)
- [ ] Monitor query performance
- [ ] Set up alerts for slow queries (>5s)
- [ ] Review performance regularly
- [ ] User feedback collection

---

## Common Performance Anti-Patterns

### ❌ The Data Firehose
```
SELECT * FROM giant_table;
-- Returns millions of rows
-- Takes 30+ seconds
-- Dashboard unusable
```
**Solution**: Aggregate, filter, limit

### ❌ The Query Waterfall
```
Dashboard with 20 charts, each independent query:
- Chart 1: 2s
- Chart 2: 2s
- Chart 3: 2s
...
Total: 40 seconds!
```
**Solution**: Single query, multiple views, or parallel queries

### ❌ The Filter Cascade of Doom
```
Auto-apply filters:
User changes 5 filters = 5 queries = 10 seconds
```
**Solution**: Apply button, single query

### ❌ The Live Connection Trap
```
Every dashboard interaction hits production database
100 users = 100 concurrent queries = database meltdown
```
**Solution**: Extracts, caching, dedicated BI database

### ❌ The Calculated Field Explosion
```
Complex calculations in dashboard repeated 10,000 times
Per row, per chart, per refresh
```
**Solution**: Pre-calculate in database or data model

---

## References
- Tableau: Performance Best Practices
- Power BI: Optimization Guide
- Google: Web Performance Best Practices
- High Performance Browser Networking
- Database Indexing Strategies
