# Database Schema Design Template

## Purpose
Use this template when designing a new database schema or refactoring an existing one.

## Step 1: Requirements Gathering

### Business Domain
- [ ] What is the application domain? (e-commerce, social network, SaaS, etc.)
- [ ] What are the core entities/concepts?
- [ ] What are the relationships between entities?

### Data Characteristics
- [ ] Expected data volume? (rows per table, total size)
- [ ] Data growth rate? (per day/month/year)
- [ ] Data retention requirements?
- [ ] Compliance requirements? (GDPR, HIPAA, SOC2)

### Access Patterns
- [ ] Read/Write ratio? (read-heavy, write-heavy, balanced)
- [ ] Query patterns? (list most common queries)
- [ ] Concurrent users/requests?
- [ ] Latency requirements? (p50, p95, p99)

### Constraints
- [ ] Budget limitations?
- [ ] Team expertise? (SQL, NoSQL, specific database systems)
- [ ] Existing infrastructure?
- [ ] Integration requirements?

## Step 2: Database Technology Selection

### Decision Matrix

| Requirement | Relational SQL | Document Store | Key-Value | Wide-Column | Graph |
|-------------|---------------|----------------|-----------|-------------|-------|
| Complex queries | ✅ Excellent | ⚠️ Limited | ❌ No | ⚠️ Limited | ✅ (for graphs) |
| Flexible schema | ❌ Rigid | ✅ Very flexible | ✅ Flexible | ✅ Flexible | ⚠️ Semi-flexible |
| ACID transactions | ✅ Strong | ⚠️ Limited | ⚠️ Limited | ❌ No | ⚠️ Limited |
| Horizontal scalability | ⚠️ Complex | ✅ Easy | ✅ Easy | ✅ Easy | ⚠️ Moderate |
| Relationships | ✅ Excellent | ⚠️ Embedded | ❌ No | ❌ No | ✅ Excellent |
| High write throughput | ⚠️ Moderate | ✅ High | ✅ Very high | ✅ Very high | ⚠️ Moderate |

### Recommendation
**Selected Database**: ________________

**Reasoning**:
-
-
-

## Step 3: Entity Modeling

### Core Entities

```
Entity: ____________
Attributes:
-
-
-

Relationships:
-
-
```

## Step 4: Schema Design (Relational)

### Table Definitions

```sql
CREATE TABLE table_name (
    id BIGSERIAL PRIMARY KEY,
    -- Attributes
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_table_column ON table_name(column);

-- Constraints
ALTER TABLE table_name ADD CONSTRAINT constraint_name CHECK (condition);
```

### Normalization Level
- [ ] 1NF (First Normal Form)
- [ ] 2NF (Second Normal Form)
- [ ] 3NF (Third Normal Form)
- [ ] BCNF (Boyce-Codd Normal Form)

**Denormalization Strategy** (if applicable):
-
-

### Partitioning Strategy
- [ ] No partitioning needed
- [ ] Range partitioning (by date, ID range)
- [ ] List partitioning (by category, region)
- [ ] Hash partitioning (for even distribution)

```sql
-- Partitioning example
CREATE TABLE orders (
    order_id BIGSERIAL NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    -- ...
) PARTITION BY RANGE (created_at);

CREATE TABLE orders_2024_01 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

## Step 5: Index Strategy

### Index Checklist
- [ ] Primary key indexes (automatic)
- [ ] Foreign key indexes
- [ ] Indexes for WHERE clause filters
- [ ] Indexes for ORDER BY columns
- [ ] Composite indexes for multi-column queries
- [ ] Partial indexes for filtered queries
- [ ] Covering indexes (INCLUDE columns)

### Index Definitions

```sql
-- Single column index
CREATE INDEX idx_name ON table(column);

-- Composite index (order matters!)
CREATE INDEX idx_name ON table(col1, col2, col3);

-- Partial index
CREATE INDEX idx_name ON table(column) WHERE condition;

-- Covering index (PostgreSQL)
CREATE INDEX idx_name ON table(col1) INCLUDE (col2, col3);
```

## Step 6: Data Integrity

### Constraints

```sql
-- NOT NULL
ALTER TABLE table_name ALTER COLUMN column SET NOT NULL;

-- UNIQUE
ALTER TABLE table_name ADD CONSTRAINT unique_column UNIQUE (column);

-- CHECK
ALTER TABLE table_name ADD CONSTRAINT check_name CHECK (condition);

-- FOREIGN KEY
ALTER TABLE child_table ADD CONSTRAINT fk_name
    FOREIGN KEY (parent_id) REFERENCES parent_table(id)
    ON DELETE CASCADE;  -- or RESTRICT, SET NULL, SET DEFAULT
```

### Triggers (if needed)

```sql
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_timestamp
BEFORE UPDATE ON table_name
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();
```

## Step 7: Performance Optimization

### Query Pattern Analysis

| Query Pattern | Frequency | Expected Rows | Optimization |
|---------------|-----------|---------------|--------------|
| | | | |
| | | | |

### Denormalization Decisions

```sql
-- Materialized view for reporting
CREATE MATERIALIZED VIEW view_name AS
SELECT /* aggregation query */
WITH DATA;

CREATE UNIQUE INDEX idx_view ON view_name(columns);

-- Refresh strategy
REFRESH MATERIALIZED VIEW CONCURRENTLY view_name;
```

### Caching Strategy
- [ ] Application-level cache (Redis, Memcached)
- [ ] Query result cache
- [ ] Computed column cache
- [ ] Materialized views

## Step 8: Scalability Planning

### Scaling Strategy
- [ ] Vertical scaling (larger instance)
- [ ] Read replicas (for read-heavy workloads)
- [ ] Connection pooling (PgBouncer, ProxySQL)
- [ ] Sharding (horizontal partitioning)

### Sharding Strategy (if applicable)
**Shard Key**: ________________

**Distribution**:
- [ ] Hash-based
- [ ] Range-based
- [ ] Geographic

## Step 9: Migration Plan

### Phase 1: Schema Creation
```sql
-- Create tables in dependency order
CREATE TABLE users (...);
CREATE TABLE orders (...);
CREATE TABLE order_items (...);
```

### Phase 2: Data Migration
```sql
-- Bulk insert from old system
INSERT INTO new_table SELECT /* transform */ FROM old_table;
```

### Phase 3: Validation
```sql
-- Row count verification
SELECT COUNT(*) FROM old_table;
SELECT COUNT(*) FROM new_table;

-- Data integrity checks
SELECT /* validation queries */;
```

## Step 10: Monitoring Setup

### Key Metrics to Track
- [ ] Query performance (p50, p95, p99)
- [ ] Table sizes and growth rate
- [ ] Index usage
- [ ] Cache hit ratio
- [ ] Connection pool utilization
- [ ] Replication lag (if applicable)

### Monitoring Queries

```sql
-- Table sizes
SELECT pg_size_pretty(pg_total_relation_size('table_name'));

-- Index usage
SELECT * FROM pg_stat_user_indexes WHERE idx_scan = 0;

-- Cache hit ratio
SELECT sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read))
FROM pg_statio_user_tables;
```

## Checklist

Before deploying to production:

- [ ] Schema design reviewed by team
- [ ] Indexes created for all query patterns
- [ ] Constraints and validations in place
- [ ] Backup strategy configured
- [ ] Monitoring and alerting set up
- [ ] Tested with production-like data volume
- [ ] Migration plan documented and tested
- [ ] Rollback procedure defined
- [ ] Security and access control configured
- [ ] Documentation updated

## Resources

- [PostgreSQL Schema Design Best Practices](https://www.postgresql.org/docs/current/ddl.html)
- [MySQL Schema Design Guide](https://dev.mysql.com/doc/refman/8.0/en/data-types.html)
- [Database Normalization Explained](https://www.databasestar.com/database-normalization/)
- [Index Design Guidelines](https://use-the-index-luke.com/)

---

**Template Version**: 1.0
**Last Updated**: 2025-11-19
