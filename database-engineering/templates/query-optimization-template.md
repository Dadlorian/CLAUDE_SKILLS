# Query Optimization Template

## Purpose
Use this template to systematically optimize slow database queries.

## Step 1: Identify the Problem

### Query Details
**Original Query**:
```sql
-- Paste your slow query here
```

**Current Performance**:
- Execution time: ________ ms
- Rows examined: ________
- Rows returned: ________
- Frequency: ________ times/second

**Performance Target**:
- Target execution time: ________ ms
- Acceptable latency (p95): ________ ms

## Step 2: Gather Context

### Database Information
- Database system: ________ (PostgreSQL, MySQL, etc.)
- Database version: ________
- Table sizes:
  - table_name: ________ rows (________ GB)
  - table_name: ________ rows (________ GB)

### Current Indexes
```sql
-- List existing indexes
-- PostgreSQL:
\d table_name

-- MySQL:
SHOW INDEX FROM table_name;
```

**Existing indexes**:
-
-

## Step 3: Analyze Execution Plan

### PostgreSQL

```sql
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, COSTS, TIMING)
-- Your query here
```

**Key findings**:
- Seq Scan on ________ (table too small for index / missing index)
- Index Scan using ________ (good!)
- Nested Loop (check row estimates)
- Hash Join (check memory usage)
- Buffers: shared hit=________ read=________ (I/O operations)

### MySQL

```sql
EXPLAIN FORMAT=JSON
-- Your query here
```

**Key findings**:
- "type": "ALL" → Full table scan (bad)
- "type": "index" → Full index scan
- "type": "range" → Index range scan (good)
- "type": "ref" → Index lookup (good)
- "Extra": "Using filesort" → Expensive sort
- "Extra": "Using temporary" → Temp table created
- "Extra": "Using index" → Covering index (excellent)

## Step 4: Apply Optimization Techniques

### Technique 1: Add Missing Indexes

**Analysis**: Query filters on ________ but no index exists

**Solution**:
```sql
-- Single column index
CREATE INDEX idx_name ON table(column);

-- Composite index (order: equality → range → sort)
CREATE INDEX idx_name ON table(col1, col2, col3);

-- Partial index (PostgreSQL)
CREATE INDEX idx_name ON table(column) WHERE condition;

-- Covering index (PostgreSQL)
CREATE INDEX idx_name ON table(col1) INCLUDE (col2, col3);

-- Functional index
CREATE INDEX idx_name ON table(LOWER(column));
```

### Technique 2: Rewrite Query

**Original query issues**:
-
-

**Optimized query**:
```sql
-- Rewritten version
```

**Common rewrites**:

```sql
-- ❌ Subquery in SELECT (runs for each row)
SELECT user_id,
       (SELECT COUNT(*) FROM orders WHERE orders.user_id = users.user_id)
FROM users;

-- ✅ JOIN with aggregation
SELECT u.user_id, COUNT(o.order_id)
FROM users u
LEFT JOIN orders o ON u.user_id = o.user_id
GROUP BY u.user_id;

-- ❌ OR conditions (prevents index usage)
SELECT * FROM users WHERE email = 'a@b.com' OR email = 'c@d.com';

-- ✅ IN clause
SELECT * FROM users WHERE email IN ('a@b.com', 'c@d.com');

-- ❌ Function on indexed column (prevents index usage)
SELECT * FROM users WHERE YEAR(created_at) = 2024;

-- ✅ Range on raw column
SELECT * FROM users
WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01';

-- ❌ Implicit type conversion
SELECT * FROM orders WHERE user_id = '123';  -- user_id is BIGINT

-- ✅ Explicit type
SELECT * FROM orders WHERE user_id = 123;

-- ❌ SELECT * (fetches unnecessary data)
SELECT * FROM users WHERE user_id = 123;

-- ✅ Select only needed columns
SELECT user_id, username, email FROM users WHERE user_id = 123;

-- ❌ OFFSET pagination (scans and discards rows)
SELECT * FROM orders ORDER BY created_at DESC LIMIT 20 OFFSET 10000;

-- ✅ Keyset pagination
SELECT * FROM orders
WHERE (created_at, order_id) < ('2024-01-15 10:30:00', 12345)
ORDER BY created_at DESC, order_id DESC
LIMIT 20;
```

### Technique 3: Optimize JOINs

**Analysis**: Join order / join type issues

**Solutions**:
```sql
-- Ensure indexes on join columns
CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_users_id ON users(user_id);  -- Usually PK

-- Reorder joins (smaller table first, if optimizer doesn't do it)
-- Statistics might be stale
ANALYZE users;
ANALYZE orders;

-- Consider JOIN type
-- INNER JOIN (only matching rows)
-- LEFT JOIN (all rows from left, matched from right)
-- Use INNER when possible (faster)
```

### Technique 4: Reduce Data Scanned

```sql
-- Add WHERE filters early
-- Use LIMIT when appropriate
-- Filter before JOIN if possible

-- ❌ Filter after aggregation
SELECT user_id, COUNT(*) as cnt
FROM orders
GROUP BY user_id
HAVING COUNT(*) > 100;

-- ✅ Filter before aggregation (if possible)
-- Depends on the logic

-- Use indexes for sorting (avoid filesort)
-- Index should match ORDER BY columns
CREATE INDEX idx_orders_created ON orders(created_at DESC);
SELECT * FROM orders ORDER BY created_at DESC LIMIT 10;
```

### Technique 5: Denormalize for Read Performance

```sql
-- Add redundant columns to avoid JOINs
ALTER TABLE orders ADD COLUMN user_email VARCHAR(320);

-- Update existing data
UPDATE orders o
SET user_email = u.email
FROM users u
WHERE o.user_id = u.user_id;

-- Maintain denormalized data with trigger
CREATE OR REPLACE FUNCTION sync_user_email()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'UPDATE' AND OLD.email != NEW.email) THEN
        UPDATE orders SET user_email = NEW.email WHERE user_id = NEW.user_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_sync_user_email
AFTER UPDATE OF email ON users
FOR EACH ROW
EXECUTE FUNCTION sync_user_email();
```

### Technique 6: Use Materialized Views

```sql
-- PostgreSQL: Create materialized view
CREATE MATERIALIZED VIEW order_stats AS
SELECT
    user_id,
    COUNT(*) as total_orders,
    SUM(total_amount) as lifetime_value,
    MAX(created_at) as last_order_date
FROM orders
GROUP BY user_id;

CREATE UNIQUE INDEX idx_order_stats_user ON order_stats(user_id);

-- Refresh strategy
REFRESH MATERIALIZED VIEW CONCURRENTLY order_stats;

-- Schedule refresh (pg_cron extension)
SELECT cron.schedule('refresh-order-stats', '0 * * * *',
    'REFRESH MATERIALIZED VIEW CONCURRENTLY order_stats');
```

## Step 5: Verify Improvement

### Before Optimization
```sql
EXPLAIN ANALYZE
-- Original query
```

**Results**:
- Execution time: ________ ms
- Planning time: ________ ms
- Buffers hit: ________ read: ________

### After Optimization
```sql
EXPLAIN ANALYZE
-- Optimized query
```

**Results**:
- Execution time: ________ ms (________ % improvement)
- Planning time: ________ ms
- Buffers hit: ________ read: ________

### Validation

- [ ] Query returns same results
- [ ] Performance meets target (< ________ ms)
- [ ] No regressions in other queries
- [ ] Index size is reasonable
- [ ] Tested with production-like data volume

## Step 6: Monitor in Production

### Metrics to Track
```sql
-- PostgreSQL: Query statistics
SELECT
    query,
    calls,
    mean_exec_time,
    max_exec_time
FROM pg_stat_statements
WHERE query LIKE '%your_table%'
ORDER BY mean_exec_time DESC;

-- Index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read
FROM pg_stat_user_indexes
WHERE tablename = 'your_table'
ORDER BY idx_scan DESC;
```

### Alerts
- [ ] Alert if p95 latency > ________ ms
- [ ] Alert if new index is not used (idx_scan = 0 after 24h)
- [ ] Alert if table bloat > 20%

## Checklist

- [ ] Execution plan analyzed
- [ ] Missing indexes identified and added
- [ ] Query rewritten for efficiency
- [ ] JOIN order optimized
- [ ] Denormalization considered (if beneficial)
- [ ] Performance improvement verified (before/after)
- [ ] Results validated (correctness)
- [ ] Monitoring configured
- [ ] Documentation updated
- [ ] Team notified of changes

## Common Pitfalls to Avoid

- ❌ Adding too many indexes (slows down writes)
- ❌ Not updating statistics after schema changes
- ❌ Optimizing for small dataset (test with production volume)
- ❌ Forgetting to monitor new indexes (unused indexes waste space)
- ❌ Breaking queries into N+1 pattern
- ❌ Over-denormalizing (data consistency issues)

## Resources

- [PostgreSQL EXPLAIN Documentation](https://www.postgresql.org/docs/current/using-explain.html)
- [MySQL EXPLAIN Documentation](https://dev.mysql.com/doc/refman/8.0/en/explain.html)
- [Use The Index, Luke](https://use-the-index-luke.com/)
- [PostgreSQL Query Optimization Tips](https://wiki.postgresql.org/wiki/Performance_Optimization)

---

**Template Version**: 1.0
**Last Updated**: 2025-11-19
