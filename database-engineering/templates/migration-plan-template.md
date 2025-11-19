# Database Migration Plan Template

## Purpose
Use this template to plan and execute database migrations safely with minimal or zero downtime.

## Migration Overview

### Migration Type
- [ ] Same database system, version upgrade (e.g., PostgreSQL 13 → 15)
- [ ] Same database system, different infrastructure (e.g., on-prem → cloud)
- [ ] Different database system (e.g., MySQL → PostgreSQL)
- [ ] Different database paradigm (e.g., SQL → NoSQL)

### Migration Details
- **Source**: ________ (database system, version, location)
- **Target**: ________ (database system, version, location)
- **Database size**: ________ GB
- **Row counts**: ________ million rows across ________ tables
- **Downtime tolerance**: ________ (none / minutes / hours)

## Step 1: Pre-Migration Assessment

### Current State Analysis
```sql
-- Database size
SELECT pg_size_pretty(pg_database_size('mydb'));

-- Table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    n_live_tup AS row_count
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Row counts
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM orders;
-- ... for all tables
```

**Largest tables**:
1. ________ (________ GB, ________ rows)
2. ________ (________ GB, ________ rows)
3. ________ (________ GB, ________ rows)

### Dependencies
- [ ] Applications using this database
- [ ] Scheduled jobs/cron tasks
- [ ] ETL pipelines
- [ ] Analytics/BI tools
- [ ] Third-party integrations
- [ ] Backup systems
- [ ] Monitoring systems

### Risk Assessment
| Risk | Impact (H/M/L) | Probability (H/M/L) | Mitigation |
|------|---------------|---------------------|------------|
| Data loss | H | L | Verify backups, test restore |
| Extended downtime | M | M | Use replication strategy |
| Application errors | H | M | Thorough testing in staging |
| Performance degradation | M | M | Load testing before cutover |

## Step 2: Migration Strategy Selection

### Strategy 1: Dump & Restore (Simplest)
**Best for**: Small databases (< 100GB), tolerate hours of downtime

**Pros**:
- Simple, straightforward
- Clean migration (no bloat)
- Easy to understand and execute

**Cons**:
- Requires downtime
- Slow for large databases

**Timeline**:
- Dump: ________ hours
- Transfer: ________ hours
- Restore: ________ hours
- Validation: ________ hours
- **Total downtime**: ________ hours

### Strategy 2: Replication & Cutover (Minimal Downtime)
**Best for**: Large databases (> 100GB), tolerate minutes of downtime

**Pros**:
- Minimal downtime (minutes)
- Can validate before cutover
- Rollback possible

**Cons**:
- More complex setup
- Requires compatible replication

**Timeline**:
- Setup replication: ________ hours
- Initial sync: ________ hours
- Validation: ________ hours
- Cutover: ________ minutes
- **Total downtime**: ________ minutes

### Strategy 3: Dual-Write (Zero Downtime)
**Best for**: Critical systems, no downtime tolerance

**Pros**:
- Zero downtime
- Gradual migration
- Easy rollback

**Cons**:
- Most complex
- Requires application changes
- Temporary data duplication

**Timeline**:
- Phase 1 (dual write): ________ days
- Phase 2 (backfill): ________ days
- Phase 3 (verification): ________ days
- Phase 4 (gradual cutover): ________ days
- Phase 5 (cleanup): ________ days
- **Total downtime**: 0 minutes

**Selected strategy**: ________________

**Reasoning**:
-
-

## Step 3: Detailed Migration Plan

### Phase 1: Preparation

#### Backups
```bash
# PostgreSQL full backup
pg_dump -h source-host -U postgres -Fc -f backup_$(date +%Y%m%d_%H%M%S).dump mydb

# Verify backup
pg_restore --list backup_*.dump | head -20

# MySQL full backup
mysqldump -h source-host -u root -p --single-transaction \
    --routines --triggers --events mydb > backup_$(date +%Y%m%d_%H%M%S).sql
```

**Backup verification**:
- [ ] Backup completed successfully
- [ ] Backup file size matches expectations
- [ ] Backup can be listed/read
- [ ] Test restore in isolated environment

#### Schema Export
```bash
# PostgreSQL schema only
pg_dump -h source-host -U postgres -s -f schema.sql mydb

# MySQL schema only
mysqldump -h source-host -u root -p --no-data mydb > schema.sql
```

#### Baseline Metrics
```sql
-- Record current state for validation
CREATE TABLE migration_baseline AS
SELECT
    'users' AS table_name,
    COUNT(*) AS row_count,
    MD5(string_agg(user_id::text, ',' ORDER BY user_id)) AS checksum
FROM users
UNION ALL
SELECT 'orders', COUNT(*), MD5(string_agg(order_id::text, ',' ORDER BY order_id))
FROM orders;
-- ... for all tables
```

### Phase 2: Migration Execution

#### Option A: Dump & Restore

```bash
# Step 1: Dump source database
pg_dump -h source-host -U postgres -Fc -j 4 -f source_dump.dump mydb

# Step 2: Transfer to target
scp source_dump.dump target-host:/tmp/

# Step 3: Restore to target
pg_restore -h target-host -U postgres -j 4 -d mydb source_dump.dump

# Step 4: Recreate indexes (if needed)
psql -h target-host -U postgres -d mydb -f recreate_indexes.sql
```

#### Option B: Replication & Cutover

```bash
# PostgreSQL replication setup (see HA template for details)

# Step 1: Setup replication from source to target
# On source:
CREATE USER replicator REPLICATION LOGIN ENCRYPTED PASSWORD 'password';

# On target:
pg_basebackup -h source-host -U replicator -D /var/lib/postgresql/data \
    -P -v -R -X stream

# Step 2: Wait for replication to catch up
psql -h target-host -c "SELECT pg_last_wal_replay_lsn()"
psql -h source-host -c "SELECT pg_current_wal_lsn()"
# Diff should be < 1MB

# Step 3: Cutover
# a. Stop application writes to source
# b. Wait for replication lag = 0
# c. Promote target to primary
pg_ctl promote -D /var/lib/postgresql/data

# d. Update application connection strings
# e. Start application
```

#### Option C: Dual-Write Migration

```javascript
// Phase 1: Dual write implementation
const oldDB = new Database({ /* old db config */ });
const newDB = new Database({ /* new db config */ });

async function createUser(userData) {
  // Write to old database (primary)
  const oldUser = await oldDB.query(
    'INSERT INTO users (username, email) VALUES ($1, $2) RETURNING *',
    [userData.username, userData.email]
  );

  // Shadow write to new database
  try {
    await newDB.query(
      'INSERT INTO users (user_id, username, email) VALUES ($1, $2, $3)',
      [oldUser.user_id, userData.username, userData.email]
    );
  } catch (err) {
    // Log but don't fail
    console.error('Shadow write failed:', err);
    metrics.increment('shadow_write_failure');
  }

  return oldUser;
}

// Phase 2: Backfill historical data
async function backfillUsers() {
  const batchSize = 1000;
  let lastId = 0;

  while (true) {
    const users = await oldDB.query(
      'SELECT * FROM users WHERE user_id > $1 ORDER BY user_id LIMIT $2',
      [lastId, batchSize]
    );

    if (users.rows.length === 0) break;

    await newDB.bulkInsert('users', users.rows);

    lastId = users.rows[users.rows.length - 1].user_id;
    console.log(`Backfilled up to user_id: ${lastId}`);

    await sleep(100); // Throttle
  }
}

// Phase 3: Verification (see Step 4)

// Phase 4: Gradual read cutover
let newDBReadPercentage = 0; // Increase from 0% to 100%

async function getUser(userId) {
  const useNewDB = Math.random() * 100 < newDBReadPercentage;
  return useNewDB ? newDB.getUser(userId) : oldDB.getUser(userId);
}

// Phase 5: Full cutover
// Stop writing to old database
```

### Phase 3: Schema Migration (if database type changes)

```sql
-- Example: MySQL → PostgreSQL conversion

-- MySQL (source):
CREATE TABLE users (
  user_id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- PostgreSQL (target):
CREATE TABLE users (
  user_id SERIAL PRIMARY KEY,  -- INT AUTO_INCREMENT → SERIAL
  username VARCHAR(50) UNIQUE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()  -- DATETIME → TIMESTAMPTZ
);

-- Data type mappings:
-- MySQL DATETIME → PostgreSQL TIMESTAMPTZ
-- MySQL INT AUTO_INCREMENT → PostgreSQL SERIAL or BIGSERIAL
-- MySQL TEXT → PostgreSQL TEXT (same)
-- MySQL ENUM → PostgreSQL VARCHAR with CHECK constraint
```

## Step 4: Validation

### Data Validation

```sql
-- Row count verification
SELECT 'users' AS table, COUNT(*) AS count FROM users
UNION ALL
SELECT 'orders', COUNT(*) FROM orders;

-- Compare with baseline (should match)

-- Checksum verification (sample)
SELECT MD5(string_agg(user_id::text || email, ',' ORDER BY user_id))
FROM users
WHERE user_id BETWEEN 1 AND 10000;

-- Spot check random samples
SELECT * FROM users WHERE user_id = 12345;  -- Compare old vs new

-- Foreign key integrity
SELECT o.order_id
FROM orders o
LEFT JOIN users u ON o.user_id = u.user_id
WHERE u.user_id IS NULL;  -- Should return 0 rows
```

### Performance Validation

```sql
-- Run critical queries and compare performance
EXPLAIN ANALYZE
SELECT u.username, COUNT(o.order_id)
FROM users u
LEFT JOIN orders o ON u.user_id = o.user_id
GROUP BY u.user_id, u.username
ORDER BY COUNT(o.order_id) DESC
LIMIT 100;

-- Compare execution time with old database
```

### Application Validation
- [ ] Run integration test suite
- [ ] Test critical user flows
- [ ] Verify read operations
- [ ] Verify write operations
- [ ] Verify transactions
- [ ] Load test (compare with baseline)

## Step 5: Cutover

### Cutover Checklist

**30 minutes before**:
- [ ] Notify team and stakeholders
- [ ] Verify backups are current
- [ ] Prepare rollback plan
- [ ] Set up monitoring dashboards
- [ ] Prepare runbook for troubleshooting

**15 minutes before**:
- [ ] Enable maintenance mode (if applicable)
- [ ] Stop scheduled jobs
- [ ] Verify no long-running queries

**Cutover (Go/No-Go Decision)**:
- [ ] Replication lag < 1MB (for replication strategy)
- [ ] All validation tests pass
- [ ] Team ready to support
- [ ] Rollback plan tested

**Cutover execution**:
1. [ ] Stop application writes (or enable read-only mode)
2. [ ] Wait for replication lag = 0 (for replication strategy)
3. [ ] Promote new database to primary (if applicable)
4. [ ] Update application configuration (connection strings)
5. [ ] Restart application with new configuration
6. [ ] Verify application health
7. [ ] Monitor error rates and latency
8. [ ] Re-enable writes
9. [ ] Re-enable scheduled jobs
10. [ ] Disable maintenance mode

**Post-cutover (first 1 hour)**:
- [ ] Monitor application metrics
- [ ] Monitor database metrics
- [ ] Check error logs
- [ ] Verify user-facing functionality
- [ ] Be ready to rollback if issues arise

## Step 6: Rollback Plan

### Rollback Criteria
Rollback if:
- Error rate > ________%
- Latency > ________ ms (p95)
- Database connection failures
- Data corruption detected
- Critical functionality broken

### Rollback Procedure
```bash
# For replication strategy:
# 1. Switch application back to old database
#    Update connection string, restart app

# 2. Verify old database is healthy
psql -h old-host -c "SELECT 1"

# 3. Disable new database
#    To prevent accidental writes

# For dual-write strategy:
# 1. Set newDBReadPercentage = 0
# 2. Stop shadow writes to new database
# 3. Continue using old database
```

## Step 7: Post-Migration

### Cleanup
- [ ] Remove old database (after ________ days)
- [ ] Remove dual-write code (after ________ days)
- [ ] Update documentation
- [ ] Update monitoring
- [ ] Update backup scripts
- [ ] Remove temporary migration tables/scripts

### Optimization
```sql
-- Update statistics
ANALYZE;

-- Rebuild indexes (if needed)
REINDEX DATABASE mydb;

-- Vacuum (PostgreSQL)
VACUUM ANALYZE;
```

### Monitoring
- [ ] Set up performance baselines for new database
- [ ] Configure alerts
- [ ] Monitor query performance
- [ ] Monitor replication (if applicable)
- [ ] Monitor disk usage

## Timeline

| Phase | Duration | Downtime |
|-------|----------|----------|
| Preparation | | 0 |
| Schema setup | | 0 |
| Data migration | | (varies) |
| Validation | | 0 |
| Cutover | | (varies) |
| Monitoring | | 0 |
| **Total** | | |

## Communication Plan

### Stakeholders
- Engineering team
- Product team
- Customer support
- Executive team

### Communication Schedule
- **T-7 days**: Announce migration plan
- **T-3 days**: Reminder, confirm timeline
- **T-1 day**: Final reminder, prepare for support
- **T-0 (cutover)**: Begin migration, status updates every 30min
- **T+1 hour**: Migration complete announcement
- **T+24 hours**: Post-migration report

## Resources

- [PostgreSQL Migration Guide](https://www.postgresql.org/docs/current/migration.html)
- [AWS Database Migration Service](https://aws.amazon.com/dms/)
- [MySQL to PostgreSQL Migration](https://www.postgresql.org/docs/current/sql-createdomain.html)
- [Zero-Downtime Migrations](https://www.braintreepayments.com/blog/safe-operations-for-high-volume-postgresql/)

---

**Template Version**: 1.0
**Last Updated**: 2025-11-19
