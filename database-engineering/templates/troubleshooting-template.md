# Database Troubleshooting Template

## Purpose
Use this template to systematically diagnose and resolve database issues.

## Issue Report

### Problem Description
**Symptom**: ________________ (slow queries, connection errors, high CPU, etc.)

**When did it start**: ________________

**Frequency**: ________________ (constant, intermittent, specific times)

**Impact**: ________________ (user-facing, internal, critical/non-critical)

### Environment
- Database system: ________________
- Version: ________________
- Infrastructure: ________________ (cloud, on-prem, managed service)
- Recent changes: ________________ (deployments, config changes, schema changes)

## Step 1: Quick Health Check

### System Resources

```bash
# CPU usage
top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1"%"}'

# Memory usage
free -h

# Disk usage
df -h

# Disk I/O
iostat -x 1 5

# Network connections
netstat -an | grep :5432 | wc -l  # PostgreSQL
netstat -an | grep :3306 | wc -l  # MySQL
```

### Database Status

```sql
-- PostgreSQL: Check if database is up
SELECT version();

-- Check active connections
SELECT count(*), state FROM pg_stat_activity GROUP BY state;

-- Check for long-running queries
SELECT
    pid,
    now() - pg_stat_activity.query_start AS duration,
    query,
    state
FROM pg_stat_activity
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes'
ORDER BY duration DESC;

-- MySQL: Check status
SHOW STATUS LIKE 'Threads_connected';
SHOW PROCESSLIST;
```

## Step 2: Common Issues & Solutions

### Issue 1: Slow Queries

#### Diagnosis

```sql
-- PostgreSQL: Find slow queries
SELECT
    query,
    calls,
    mean_exec_time,
    max_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Analyze specific query
EXPLAIN (ANALYZE, BUFFERS)
SELECT /* your slow query */;

-- MySQL: Find slow queries
SELECT
    DIGEST_TEXT,
    AVG_TIMER_WAIT/1000000000000 AS avg_sec
FROM performance_schema.events_statements_summary_by_digest
ORDER BY AVG_TIMER_WAIT DESC
LIMIT 10;

-- Analyze specific query
EXPLAIN FORMAT=JSON
SELECT /* your slow query */;
```

#### Solution Checklist
- [ ] Check execution plan for full table scans
- [ ] Verify indexes exist for WHERE/JOIN columns
- [ ] Update table statistics (ANALYZE table_name)
- [ ] Consider adding indexes
- [ ] Rewrite query if using anti-patterns
- [ ] Check if problem is data volume (pagination needed)

### Issue 2: High CPU Usage

#### Diagnosis

```bash
# Identify CPU-intensive queries
# PostgreSQL:
sudo -u postgres psql <<EOF
SELECT
    pid,
    query,
    state,
    (now() - query_start) AS duration
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY query_start;
EOF

# Check for vacuum/analyze processes
ps aux | grep -E "vacuum|analyze"

# MySQL:
mysql -e "SHOW FULL PROCESSLIST"
```

#### Solution Checklist
- [ ] Identify and optimize expensive queries
- [ ] Check for missing indexes causing full table scans
- [ ] Verify autovacuum is not overwhelmed (PostgreSQL)
- [ ] Check for complex aggregations or sorts
- [ ] Consider query result caching
- [ ] Scale vertically (more CPU) if queries are optimal

### Issue 3: Connection Pool Exhausted

#### Diagnosis

```sql
-- PostgreSQL: Check connections
SELECT
    count(*) AS total,
    sum(case when state = 'active' then 1 else 0 end) AS active,
    sum(case when state = 'idle' then 1 else 0 end) AS idle,
    sum(case when state = 'idle in transaction' then 1 else 0 end) AS idle_in_txn
FROM pg_stat_activity;

-- Find long idle connections
SELECT
    pid,
    usename,
    application_name,
    client_addr,
    state,
    state_change
FROM pg_stat_activity
WHERE state = 'idle in transaction'
  AND state_change < now() - interval '10 minutes'
ORDER BY state_change;

-- MySQL: Check connections
SHOW STATUS LIKE 'Threads_connected';
SHOW VARIABLES LIKE 'max_connections';

SELECT * FROM information_schema.processlist
WHERE command = 'Sleep' AND time > 300;
```

#### Solution Checklist
- [ ] Find and fix connection leaks in application code
- [ ] Implement connection pooling (PgBouncer, ProxySQL)
- [ ] Set connection timeouts
- [ ] Kill idle connections
- [ ] Increase max_connections (if appropriate)
- [ ] Review application connection management

```sql
-- Kill idle connections (PostgreSQL)
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle in transaction'
  AND state_change < now() - interval '30 minutes';

-- MySQL:
KILL <process_id>;
```

### Issue 4: Deadlocks

#### Diagnosis

```sql
-- PostgreSQL: Enable deadlock logging
ALTER SYSTEM SET log_lock_waits = on;
ALTER SYSTEM SET deadlock_timeout = '1s';
SELECT pg_reload_conf();

-- Check for blocked queries
SELECT
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS blocking_statement
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks
    ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
    AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;

-- MySQL: Check InnoDB status
SHOW ENGINE INNODB STATUS\G
-- Look for "LATEST DETECTED DEADLOCK" section
```

#### Solution Checklist
- [ ] Identify deadlock pattern from logs
- [ ] Ensure consistent lock ordering in application
- [ ] Use SELECT FOR UPDATE to explicitly lock rows
- [ ] Keep transactions short
- [ ] Retry failed transactions with exponential backoff
- [ ] Consider using optimistic locking instead

### Issue 5: High Replication Lag

#### Diagnosis

```sql
-- PostgreSQL (on primary):
SELECT
    client_addr,
    application_name,
    pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS lag_bytes,
    extract(epoch from (now() - pg_last_xact_replay_timestamp())) AS lag_seconds
FROM pg_stat_replication;

-- On replica:
SELECT
    now() - pg_last_xact_replay_timestamp() AS lag,
    pg_is_in_recovery();

-- Check for long-running queries blocking replay
SELECT pid, query_start, query
FROM pg_stat_activity
WHERE pg_backend_pid() != pid
ORDER BY query_start;

-- MySQL (on replica):
SHOW SLAVE STATUS\G
-- Check: Seconds_Behind_Master
```

#### Solution Checklist
- [ ] Check network bandwidth between primary and replica
- [ ] Identify long-running queries on replica
- [ ] Check disk I/O on replica
- [ ] Tune replication parameters (max_standby_streaming_delay)
- [ ] Consider parallel replication (MySQL)
- [ ] Check for large transactions on primary
- [ ] Verify replica hardware is adequate

```sql
-- PostgreSQL: Tune replication
-- On replica postgresql.conf:
max_standby_streaming_delay = 30s
hot_standby_feedback = on

-- MySQL: Enable parallel replication
SET GLOBAL slave_parallel_workers = 4;
SET GLOBAL slave_parallel_type = 'LOGICAL_CLOCK';
```

### Issue 6: Table Bloat

#### Diagnosis

```sql
-- PostgreSQL: Check table bloat
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    n_dead_tup,
    n_live_tup,
    round(100 * n_dead_tup / nullif(n_live_tup + n_dead_tup, 0), 2) AS dead_pct
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;

-- Check last vacuum/analyze
SELECT
    schemaname,
    tablename,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
ORDER BY last_autovacuum NULLS FIRST;

-- MySQL: Check table fragmentation
SELECT
    table_schema,
    table_name,
    data_free / 1024 / 1024 AS fragmentation_mb
FROM information_schema.tables
WHERE table_schema NOT IN ('information_schema', 'mysql')
  AND data_free > 0
ORDER BY data_free DESC;
```

#### Solution Checklist
- [ ] Run VACUUM (PostgreSQL) or OPTIMIZE TABLE (MySQL)
- [ ] Tune autovacuum settings
- [ ] Consider VACUUM FULL for severe bloat (requires lock)
- [ ] Increase autovacuum workers
- [ ] Reduce autovacuum thresholds for large tables

```sql
-- PostgreSQL: Manual vacuum
VACUUM ANALYZE tablename;

-- Aggressive vacuum (locks table)
VACUUM FULL tablename;

-- Tune autovacuum for specific table
ALTER TABLE large_table SET (
    autovacuum_vacuum_scale_factor = 0.05,
    autovacuum_analyze_scale_factor = 0.02
);

-- MySQL: Optimize table
OPTIMIZE TABLE tablename;
```

### Issue 7: Disk Space Full

#### Diagnosis

```bash
# Check disk usage
df -h

# Find large files
du -sh /var/lib/postgresql/* | sort -rh | head -20

# PostgreSQL: Check WAL files
ls -lh /var/lib/postgresql/15/main/pg_wal/

# Check database sizes
sudo -u postgres psql -c "SELECT datname, pg_size_pretty(pg_database_size(datname)) FROM pg_database ORDER BY pg_database_size(datname) DESC;"
```

#### Solution Checklist
- [ ] Clean up old WAL files (check archive settings)
- [ ] Drop unnecessary databases/tables
- [ ] Vacuum to reclaim space
- [ ] Move WAL to separate disk
- [ ] Increase disk size
- [ ] Set up monitoring alerts for disk space

```sql
-- PostgreSQL: Check WAL settings
SHOW wal_keep_size;
SHOW archive_command;

-- Cleanup old archived WAL (be careful!)
-- Only if you have verified backups
find /mnt/wal_archive/ -name "*.backup" -mtime +7 -delete
```

## Step 3: Gather Diagnostic Information

### For Support/Team

```bash
# System information
uname -a
lscpu
free -h
df -h

# Database version
sudo -u postgres psql -c "SELECT version();"

# Configuration
sudo -u postgres psql -c "SHOW ALL;"

# Current activity
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"

# Recent errors (check logs)
tail -100 /var/log/postgresql/postgresql-*.log
```

### Export Query Statistics

```sql
-- PostgreSQL: Export slow queries
\copy (SELECT query, calls, mean_exec_time, max_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 50) TO '/tmp/slow_queries.csv' CSV HEADER;

-- Export table statistics
\copy (SELECT * FROM pg_stat_user_tables) TO '/tmp/table_stats.csv' CSV HEADER;
```

## Step 4: Preventive Measures

### Monitoring Setup
- [ ] Set up query performance monitoring
- [ ] Configure connection pool monitoring
- [ ] Set up replication lag alerts
- [ ] Monitor disk space usage
- [ ] Track cache hit ratio
- [ ] Alert on deadlocks

### Regular Maintenance
- [ ] Schedule regular VACUUM (PostgreSQL)
- [ ] Update statistics regularly (ANALYZE)
- [ ] Review slow query log weekly
- [ ] Check index usage monthly
- [ ] Review and optimize configuration quarterly
- [ ] Test disaster recovery annually

### Documentation
- [ ] Document incident for post-mortem
- [ ] Update runbooks
- [ ] Share learnings with team
- [ ] Improve monitoring based on incident

## Troubleshooting Flowchart

```
Issue Detected
    ↓
Quick Health Check
    ↓
Is DB responding? → NO → Check if process running → Start DB
    ↓ YES
Check resource usage (CPU/Memory/Disk)
    ↓
High CPU? → YES → Identify expensive queries → Optimize
    ↓ NO
High Memory? → YES → Check for memory leaks, connection leaks
    ↓ NO
Disk full? → YES → Clean up space, increase disk
    ↓ NO
Slow queries? → YES → Check execution plans, add indexes
    ↓ NO
Connection issues? → YES → Check pool, max_connections, network
    ↓ NO
Replication lag? → YES → Check network, long txns, disk I/O
    ↓ NO
Escalate to DBA team
```

## Checklist

- [ ] Issue clearly defined
- [ ] Health check completed
- [ ] Logs reviewed
- [ ] Metrics analyzed
- [ ] Root cause identified
- [ ] Solution implemented
- [ ] Verification completed
- [ ] Monitoring improved
- [ ] Documentation updated
- [ ] Post-mortem scheduled (for major incidents)

## Resources

- [PostgreSQL Troubleshooting](https://www.postgresql.org/docs/current/performance-tips.html)
- [MySQL Troubleshooting](https://dev.mysql.com/doc/refman/8.0/en/problems.html)
- [Database Reliability Engineering (O'Reilly)](https://www.oreilly.com/library/view/database-reliability-engineering/9781491925935/)

---

**Template Version**: 1.0
**Last Updated**: 2025-11-19
