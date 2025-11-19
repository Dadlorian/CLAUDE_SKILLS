# Database Monitoring Setup Template

## Purpose
Use this template to implement comprehensive database monitoring, alerting, and observability.

## Monitoring Strategy

### Golden Signals for Databases

1. **Latency**: Query response times
2. **Traffic**: Queries per second, connections
3. **Errors**: Failed queries, connection errors
4. **Saturation**: CPU, memory, disk I/O, connection pool usage

### Monitoring Stack Selection

| Tool | Best For | Complexity | Cost |
|------|----------|------------|------|
| CloudWatch (AWS) | AWS RDS | Low | $ |
| Datadog | Full-stack observability | Low-Med | $$$ |
| Prometheus + Grafana | Self-hosted, customizable | Medium | $ (OSS) |
| New Relic | APM + Database | Low | $$$ |
| Percona PMM | MySQL/PostgreSQL specialist | Medium | $ (OSS) |

**Selected stack**: ________________

## Step 1: Metrics Collection

### PostgreSQL with Prometheus

```bash
# Install postgres_exporter
wget https://github.com/prometheus-community/postgres_exporter/releases/download/v0.15.0/postgres_exporter-0.15.0.linux-amd64.tar.gz
tar xvfz postgres_exporter-0.15.0.linux-amd64.tar.gz
sudo mv postgres_exporter-0.15.0.linux-amd64/postgres_exporter /usr/local/bin/

# Create monitoring user
sudo -u postgres psql <<EOF
CREATE USER postgres_exporter WITH PASSWORD 'secure_password';
GRANT pg_monitor TO postgres_exporter;
EOF

# Configure postgres_exporter
cat > /etc/default/postgres_exporter <<EOF
DATA_SOURCE_NAME="postgresql://postgres_exporter:secure_password@localhost:5432/postgres?sslmode=disable"
EOF

# Create systemd service
cat > /etc/systemd/system/postgres_exporter.service <<EOF
[Unit]
Description=Prometheus PostgreSQL Exporter
After=network.target

[Service]
Type=simple
User=postgres
EnvironmentFile=/etc/default/postgres_exporter
ExecStart=/usr/local/bin/postgres_exporter
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable postgres_exporter
sudo systemctl start postgres_exporter
```

```yaml
# prometheus.yml - Add scrape config
scrape_configs:
  - job_name: 'postgres'
    static_configs:
      - targets: ['localhost:9187']
        labels:
          instance: 'db-primary'
```

### MySQL with Prometheus

```bash
# Install mysqld_exporter
wget https://github.com/prometheus/mysqld_exporter/releases/download/v0.15.1/mysqld_exporter-0.15.1.linux-amd64.tar.gz
tar xvfz mysqld_exporter-0.15.1.linux-amd64.tar.gz
sudo mv mysqld_exporter-0.15.1.linux-amd64/mysqld_exporter /usr/local/bin/

# Create monitoring user
mysql -u root -p <<EOF
CREATE USER 'mysqld_exporter'@'localhost' IDENTIFIED BY 'secure_password';
GRANT PROCESS, REPLICATION CLIENT, SELECT ON *.* TO 'mysqld_exporter'@'localhost';
FLUSH PRIVILEGES;
EOF

# Configure mysqld_exporter
cat > /etc/.mysqld_exporter.cnf <<EOF
[client]
user=mysqld_exporter
password=secure_password
EOF

chmod 600 /etc/.mysqld_exporter.cnf

# Create systemd service
cat > /etc/systemd/system/mysqld_exporter.service <<EOF
[Unit]
Description=Prometheus MySQL Exporter
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/mysqld_exporter --config.my-cnf=/etc/.mysqld_exporter.cnf
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable mysqld_exporter
sudo systemctl start mysqld_exporter
```

## Step 2: Key Metrics to Track

### Query Performance

```sql
-- PostgreSQL: Enable pg_stat_statements
CREATE EXTENSION pg_stat_statements;

-- Configure postgresql.conf
shared_preload_libraries = 'pg_stat_statements'
pg_stat_statements.track = all
pg_stat_statements.max = 10000

-- Query slow queries
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    stddev_exec_time,
    min_exec_time,
    max_exec_time,
    rows
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;

-- MySQL: Enable performance schema
UPDATE performance_schema.setup_instruments
SET ENABLED = 'YES', TIMED = 'YES';

UPDATE performance_schema.setup_consumers
SET ENABLED = 'YES';

-- Query slow queries
SELECT
    DIGEST_TEXT,
    COUNT_STAR AS exec_count,
    AVG_TIMER_WAIT/1000000000000 AS avg_sec,
    MAX_TIMER_WAIT/1000000000000 AS max_sec,
    SUM_ROWS_EXAMINED AS rows_examined,
    SUM_ROWS_SENT AS rows_sent
FROM performance_schema.events_statements_summary_by_digest
ORDER BY AVG_TIMER_WAIT DESC
LIMIT 20;
```

### Connection Metrics

```sql
-- PostgreSQL: Active connections
SELECT
    count(*) AS total,
    sum(case when state = 'active' then 1 else 0 end) AS active,
    sum(case when state = 'idle' then 1 else 0 end) AS idle,
    sum(case when state = 'idle in transaction' then 1 else 0 end) AS idle_in_transaction
FROM pg_stat_activity
WHERE datname IS NOT NULL;

-- MySQL: Connection stats
SHOW STATUS LIKE 'Threads_%';
SHOW STATUS LIKE 'Max_used_connections';
SHOW VARIABLES LIKE 'max_connections';
```

### Cache Hit Ratio

```sql
-- PostgreSQL: Cache hit ratio (should be > 99%)
SELECT
    sum(heap_blks_read) AS heap_read,
    sum(heap_blks_hit) AS heap_hit,
    sum(heap_blks_hit) / nullif(sum(heap_blks_hit) + sum(heap_blks_read), 0) AS cache_hit_ratio
FROM pg_statio_user_tables;

-- MySQL: Buffer pool hit ratio (should be > 99%)
SHOW STATUS LIKE 'Innodb_buffer_pool%';
-- Calculate: (Innodb_buffer_pool_read_requests - Innodb_buffer_pool_reads) / Innodb_buffer_pool_read_requests
```

### Replication Lag

```sql
-- PostgreSQL (on primary)
SELECT
    client_addr,
    application_name,
    pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS lag_bytes,
    extract(epoch from (now() - pg_last_xact_replay_timestamp())) AS lag_seconds
FROM pg_stat_replication;

-- MySQL (on replica)
SHOW SLAVE STATUS\G
-- Check: Seconds_Behind_Master
```

### Disk Usage

```sql
-- PostgreSQL: Database sizes
SELECT
    datname,
    pg_size_pretty(pg_database_size(datname)) AS size
FROM pg_database
ORDER BY pg_database_size(datname) DESC;

-- Table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) AS index_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 20;

-- MySQL: Table sizes
SELECT
    table_schema,
    table_name,
    ROUND((data_length + index_length) / 1024 / 1024, 2) AS size_mb
FROM information_schema.tables
WHERE table_schema NOT IN ('information_schema', 'mysql', 'performance_schema', 'sys')
ORDER BY (data_length + index_length) DESC
LIMIT 20;
```

## Step 3: Grafana Dashboards

### Import Community Dashboards

```bash
# PostgreSQL dashboard IDs:
# - 9628: PostgreSQL Database
# - 9614: PostgreSQL Overview

# MySQL dashboard IDs:
# - 7362: MySQL Overview
# - 6239: MySQL InnoDB Metrics

# Import via Grafana UI or API
curl -X POST http://admin:password@localhost:3000/api/dashboards/import \
  -H "Content-Type: application/json" \
  -d '{"dashboard":{"id":null},"folderId":0,"inputs":[{"name":"DS_PROMETHEUS","type":"datasource","pluginId":"prometheus","value":"Prometheus"}],"overwrite":true,"pluginId":"grafana-piechart-panel","uid":"postgres-overview","version":1}'
```

### Custom Dashboard Panels

**Query Latency (p50, p95, p99)**:
```promql
# PromQL query
histogram_quantile(0.50, rate(pg_stat_statements_mean_time_bucket[5m]))
histogram_quantile(0.95, rate(pg_stat_statements_mean_time_bucket[5m]))
histogram_quantile(0.99, rate(pg_stat_statements_mean_time_bucket[5m]))
```

**Queries Per Second**:
```promql
rate(pg_stat_database_xact_commit[1m]) + rate(pg_stat_database_xact_rollback[1m])
```

**Connection Pool Usage**:
```promql
pg_stat_activity_count / pg_settings_max_connections
```

**Cache Hit Ratio**:
```promql
pg_stat_database_blks_hit / (pg_stat_database_blks_hit + pg_stat_database_blks_read)
```

## Step 4: Alerting Rules

### Prometheus Alerts

```yaml
# alerts/database.yml

groups:
  - name: database_alerts
    interval: 30s
    rules:
      # Query Performance
      - alert: SlowQueryLatency
        expr: pg_stat_statements_mean_time_seconds > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Slow query detected"
          description: "Query {{ $labels.query }} avg latency is {{ $value }}s"

      # Connection Pool
      - alert: HighConnectionUsage
        expr: (pg_stat_activity_count / pg_settings_max_connections) > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High connection usage"
          description: "{{ $value | humanizePercentage }} of max connections in use"

      - alert: ConnectionPoolExhausted
        expr: (pg_stat_activity_count / pg_settings_max_connections) > 0.95
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Connection pool near exhaustion"

      # Cache Performance
      - alert: LowCacheHitRatio
        expr: (pg_stat_database_blks_hit / (pg_stat_database_blks_hit + pg_stat_database_blks_read)) < 0.99
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Low cache hit ratio"
          description: "Cache hit ratio is {{ $value | humanizePercentage }}"

      # Replication
      - alert: ReplicationLagHigh
        expr: pg_replication_lag_seconds > 60
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High replication lag"
          description: "Replication lag is {{ $value }}s"

      - alert: ReplicaDown
        expr: up{job="postgres-replica"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Database replica is down"

      # Disk Space
      - alert: LowDiskSpace
        expr: (node_filesystem_avail_bytes{mountpoint="/var/lib/postgresql"} / node_filesystem_size_bytes{mountpoint="/var/lib/postgresql"}) < 0.2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Low disk space"
          description: "Only {{ $value | humanizePercentage }} disk space remaining"

      - alert: CriticalDiskSpace
        expr: (node_filesystem_avail_bytes{mountpoint="/var/lib/postgresql"} / node_filesystem_size_bytes{mountpoint="/var/lib/postgresql"}) < 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Critical disk space"

      # Deadlocks
      - alert: DeadlocksDetected
        expr: rate(pg_stat_database_deadlocks[5m]) > 0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Database deadlocks detected"
          description: "{{ $value }} deadlocks/sec"

      # Table Bloat
      - alert: HighTableBloat
        expr: pg_stat_user_tables_n_dead_tup / (pg_stat_user_tables_n_live_tup + pg_stat_user_tables_n_dead_tup) > 0.2
        for: 30m
        labels:
          severity: warning
        annotations:
          summary: "High table bloat"
          description: "Table {{ $labels.table }} has {{ $value | humanizePercentage }} dead tuples"
```

### Alertmanager Configuration

```yaml
# alertmanager.yml

global:
  resolve_timeout: 5m

route:
  group_by: ['alertname', 'cluster']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'team-db'
  routes:
    - match:
        severity: critical
      receiver: 'team-db-pagerduty'
      continue: true
    - match:
        severity: warning
      receiver: 'team-db-slack'

receivers:
  - name: 'team-db'
    email_configs:
      - to: 'db-team@example.com'

  - name: 'team-db-pagerduty'
    pagerduty_configs:
      - service_key: 'YOUR_PAGERDUTY_KEY'

  - name: 'team-db-slack'
    slack_configs:
      - api_url: 'YOUR_SLACK_WEBHOOK'
        channel: '#db-alerts'
        text: '{{ range .Alerts }}{{ .Annotations.summary }}\n{{ .Annotations.description }}\n{{ end }}'
```

## Step 5: Application-Level Monitoring

### SQL Query Tracing

```javascript
// Node.js with pg library
const { Pool } = require('pg');
const pool = new Pool({ /* config */ });

// Wrap query function with monitoring
const originalQuery = pool.query.bind(pool);

pool.query = function(sql, params, callback) {
  const start = Date.now();
  const queryText = typeof sql === 'string' ? sql : sql.text;

  return originalQuery(sql, params, callback).then(result => {
    const duration = Date.now() - start;

    // Log slow queries
    if (duration > 1000) {
      console.warn('Slow query detected:', {
        query: queryText,
        duration,
        rows: result.rowCount
      });

      // Send to monitoring system
      metrics.histogram('db.query.duration', duration, { slow: true });
    }

    // Track all queries
    metrics.histogram('db.query.duration', duration);
    metrics.increment('db.query.count');

    return result;
  }).catch(err => {
    metrics.increment('db.query.error');
    throw err;
  });
};
```

### Connection Pool Monitoring

```javascript
// Monitor pool events
pool.on('connect', () => {
  metrics.increment('db.pool.connect');
});

pool.on('acquire', () => {
  metrics.gauge('db.pool.active', pool.totalCount - pool.idleCount);
});

pool.on('remove', () => {
  metrics.increment('db.pool.remove');
});

pool.on('error', (err) => {
  metrics.increment('db.pool.error');
  console.error('Pool error:', err);
});

// Periodic pool stats
setInterval(() => {
  metrics.gauge('db.pool.total', pool.totalCount);
  metrics.gauge('db.pool.idle', pool.idleCount);
  metrics.gauge('db.pool.waiting', pool.waitingCount);
}, 10000);
```

## Step 6: Log Aggregation

### Configure Database Logging

```ini
# PostgreSQL postgresql.conf
logging_collector = on
log_directory = '/var/log/postgresql'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_rotation_age = 1d
log_rotation_size = 100MB

log_min_duration_statement = 1000  # Log queries > 1s
log_line_prefix = '%t [%p] %u@%d '
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on
log_temp_files = 0  # Log all temp files
```

### Ship Logs to Elasticsearch

```yaml
# filebeat.yml

filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/postgresql/*.log
    multiline.pattern: '^\d{4}-\d{2}-\d{2}'
    multiline.negate: true
    multiline.match: after

output.elasticsearch:
  hosts: ["localhost:9200"]
  index: "postgres-logs-%{+yyyy.MM.dd}"

# Or output to Logstash
output.logstash:
  hosts: ["localhost:5044"]
```

## Checklist

- [ ] Metrics exporter installed and running
- [ ] Prometheus scraping metrics
- [ ] Grafana dashboards configured
- [ ] Alert rules defined
- [ ] Alertmanager configured (email, Slack, PagerDuty)
- [ ] Application-level monitoring implemented
- [ ] Log aggregation configured
- [ ] Runbooks created for common alerts
- [ ] On-call rotation defined
- [ ] Monitoring tested (trigger test alerts)

## Resources

- [Prometheus PostgreSQL Exporter](https://github.com/prometheus-community/postgres_exporter)
- [MySQL Exporter](https://github.com/prometheus/mysqld_exporter)
- [Grafana Dashboards](https://grafana.com/grafana/dashboards/)
- [PostgreSQL Monitoring Queries](https://github.com/nilenso/postgresql-monitoring)

---

**Template Version**: 1.0
**Last Updated**: 2025-11-19
