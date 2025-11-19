# High Availability Setup Template

## Purpose
Use this template to implement high availability and disaster recovery for your database systems.

## HA Overview

### Requirements
- **Uptime SLA**: ________% (e.g., 99.9% = 43.8 min/month downtime)
- **RTO** (Recovery Time Objective): ________ (max downtime)
- **RPO** (Recovery Point Objective): ________ (max data loss)
- **Geographic requirements**: Single region / Multi-region
- **Read/Write workload**: ________% reads, ________% writes

### HA Architecture Selection

| Architecture | Uptime | Complexity | Cost | RPO | RTO |
|--------------|--------|------------|------|-----|-----|
| Single instance + backups | 99% | Low | $ | Hours | Hours |
| Primary + Standby (sync) | 99.9% | Medium | $$ | 0 | Minutes |
| Primary + Standby (async) | 99.9% | Medium | $$ | Seconds | Minutes |
| Primary + Multiple Replicas | 99.95% | Medium | $$$ | Seconds | Seconds |
| Multi-Primary (Active-Active) | 99.99% | High | $$$$ | 0 | Seconds |

**Selected architecture**: ________________

## Step 1: Replication Setup

### PostgreSQL Streaming Replication

#### On Primary Server

```bash
# 1. Configure postgresql.conf
cat >> /etc/postgresql/15/main/postgresql.conf <<EOF
# Replication settings
wal_level = replica
max_wal_senders = 10
max_replication_slots = 10
wal_keep_size = 1GB  # Minimum WAL to keep
hot_standby = on
hot_standby_feedback = on

# Archive WAL for PITR
archive_mode = on
archive_command = 'test ! -f /mnt/wal_archive/%f && cp %p /mnt/wal_archive/%f'
EOF

# 2. Create replication user
sudo -u postgres psql <<EOF
CREATE USER replicator REPLICATION LOGIN ENCRYPTED PASSWORD 'strong_password_here';
EOF

# 3. Configure pg_hba.conf
cat >> /etc/postgresql/15/main/pg_hba.conf <<EOF
# Allow replication connections
host    replication     replicator      10.0.1.0/24            scram-sha-256
host    replication     replicator      10.0.2.0/24            scram-sha-256
EOF

# 4. Restart PostgreSQL
sudo systemctl restart postgresql

# 5. Verify configuration
sudo -u postgres psql -c "SHOW wal_level;"
sudo -u postgres psql -c "SELECT * FROM pg_create_physical_replication_slot('replica1_slot');"
```

#### On Replica Server(s)

```bash
# 1. Stop PostgreSQL if running
sudo systemctl stop postgresql

# 2. Remove existing data directory
sudo rm -rf /var/lib/postgresql/15/main/*

# 3. Take base backup from primary
sudo -u postgres pg_basebackup \
    -h primary-host \
    -D /var/lib/postgresql/15/main \
    -U replicator \
    -P -v -R -X stream -C -S replica1_slot

# 4. Configure recovery settings (auto-created by -R flag)
# Verify /var/lib/postgresql/15/main/postgresql.auto.conf contains:
#   primary_conninfo = 'host=primary-host port=5432 user=replicator password=...'
#   primary_slot_name = 'replica1_slot'

# 5. Start PostgreSQL
sudo systemctl start postgresql

# 6. Verify replication status
# On primary:
sudo -u postgres psql -c "SELECT * FROM pg_stat_replication;"

# On replica:
sudo -u postgres psql -c "SELECT pg_is_in_recovery();"  # Should return true
sudo -u postgres psql -c "SELECT pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn();"
```

### MySQL Replication (GTID)

#### On Primary Server

```sql
-- 1. Configure my.cnf
[mysqld]
server_id = 1
log_bin = mysql-bin
binlog_format = ROW
gtid_mode = ON
enforce_gtid_consistency = ON
binlog_do_db = mydb  # Optional: specific database

-- 2. Restart MySQL
-- sudo systemctl restart mysql

-- 3. Create replication user
CREATE USER 'replicator'@'%' IDENTIFIED BY 'strong_password_here';
GRANT REPLICATION SLAVE ON *.* TO 'replicator'@'%';
FLUSH PRIVILEGES;

-- 4. Verify GTID is enabled
SHOW VARIABLES LIKE 'gtid_mode';
SHOW MASTER STATUS;
```

#### On Replica Server(s)

```sql
-- 1. Configure my.cnf
[mysqld]
server_id = 2  -- Unique for each replica
relay_log = relay-bin
gtid_mode = ON
enforce_gtid_consistency = ON
read_only = ON  -- Prevent writes to replica
super_read_only = ON

-- 2. Restart MySQL
-- sudo systemctl restart mysql

-- 3. Configure replication
CHANGE MASTER TO
    MASTER_HOST='primary-host',
    MASTER_USER='replicator',
    MASTER_PASSWORD='strong_password_here',
    MASTER_AUTO_POSITION=1;

-- 4. Start replication
START SLAVE;

-- 5. Verify replication status
SHOW SLAVE STATUS\G

-- Check:
-- Slave_IO_Running: Yes
-- Slave_SQL_Running: Yes
-- Seconds_Behind_Master: 0 (or low number)
```

## Step 2: Automated Failover

### Option 1: Patroni (PostgreSQL)

```yaml
# /etc/patroni/patroni.yml
scope: postgres-cluster
namespace: /service/
name: node1  # Unique per node

restapi:
  listen: 0.0.0.0:8008
  connect_address: 10.0.1.1:8008

etcd:
  hosts: 10.0.1.10:2379,10.0.1.11:2379,10.0.1.12:2379

bootstrap:
  dcs:
    ttl: 30
    loop_wait: 10
    retry_timeout: 10
    maximum_lag_on_failover: 1048576  # 1MB
    postgresql:
      use_pg_rewind: true
      parameters:
        max_connections: 200
        shared_buffers: 8GB
        effective_cache_size: 24GB
        wal_level: replica
        max_wal_senders: 10
        hot_standby: on

postgresql:
  listen: 0.0.0.0:5432
  connect_address: 10.0.1.1:5432
  data_dir: /var/lib/postgresql/15/main
  bin_dir: /usr/lib/postgresql/15/bin
  authentication:
    replication:
      username: replicator
      password: strong_password
    superuser:
      username: postgres
      password: strong_password
  parameters:
    unix_socket_directories: /var/run/postgresql

tags:
  nofailover: false
  noloadbalance: false
  clonefrom: false
```

```bash
# Install Patroni
sudo apt install -y python3-pip python3-psycopg2
sudo pip3 install patroni[etcd]

# Start Patroni
sudo systemctl enable patroni
sudo systemctl start patroni

# Check cluster status
patronictl -c /etc/patroni/patroni.yml list

# Trigger manual failover
patronictl -c /etc/patroni/patroni.yml failover
```

### Option 2: ProxySQL (MySQL Load Balancing & Failover)

```sql
-- Install ProxySQL
-- sudo apt install proxysql

-- Configure ProxySQL
-- /etc/proxysql.cnf

mysql_servers =
(
    { address="primary-host" , port=3306 , hostgroup=0, max_connections=100 },
    { address="replica1-host" , port=3306 , hostgroup=1, max_connections=100 },
    { address="replica2-host" , port=3306 , hostgroup=1, max_connections=100 }
)

mysql_users =
(
    { username = "app_user" , password = "password" , default_hostgroup = 0 , active = 1 }
)

mysql_query_rules =
(
    {
        rule_id=1
        active=1
        match_pattern="^SELECT .* FOR UPDATE$"
        destination_hostgroup=0  -- Write queries to primary
        apply=1
    },
    {
        rule_id=2
        active=1
        match_pattern="^SELECT"
        destination_hostgroup=1  -- Read queries to replicas
        apply=1
    }
)

-- Start ProxySQL
-- sudo systemctl restart proxysql

-- Verify configuration
-- mysql -h 127.0.0.1 -P 6032 -u admin -p
SELECT * FROM mysql_servers;
SELECT * FROM stats_mysql_connection_pool;
```

## Step 3: Connection Management

### Connection Pooling with PgBouncer

```ini
# /etc/pgbouncer/pgbouncer.ini

[databases]
mydb = host=localhost port=5432 dbname=mydb

[pgbouncer]
listen_addr = *
listen_port = 6432
auth_type = scram-sha-256
auth_file = /etc/pgbouncer/userlist.txt

# Pool configuration
pool_mode = transaction  # transaction | session | statement
max_client_conn = 10000
default_pool_size = 25
reserve_pool_size = 10
reserve_pool_timeout = 5

# Timeouts
server_idle_timeout = 600
server_lifetime = 3600
server_connect_timeout = 15
query_timeout = 0
query_wait_timeout = 120

# Logging
log_connections = 1
log_disconnections = 1
log_pooler_errors = 1
```

```bash
# Create userlist.txt (username password format)
echo '"app_user" "md5..."' > /etc/pgbouncer/userlist.txt

# Start PgBouncer
sudo systemctl enable pgbouncer
sudo systemctl start pgbouncer

# Monitor
psql -h localhost -p 6432 -U pgbouncer -d pgbouncer
SHOW POOLS;
SHOW CLIENTS;
SHOW SERVERS;
```

### Application Configuration

```javascript
// Node.js with multiple connection pools
const { Pool } = require('pg');

// Primary (write) pool
const primaryPool = new Pool({
  host: 'pgbouncer-primary',
  port: 6432,
  database: 'mydb',
  user: 'app_user',
  password: process.env.DB_PASSWORD,
  max: 20,  // Connection pool size
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000
});

// Replica (read) pool
const replicaPools = [
  new Pool({ host: 'pgbouncer-replica1', port: 6432, /* ... */ }),
  new Pool({ host: 'pgbouncer-replica2', port: 6432, /* ... */ }),
  new Pool({ host: 'pgbouncer-replica3', port: 6432, /* ... */ })
];

let replicaIndex = 0;

function getReadPool() {
  const pool = replicaPools[replicaIndex];
  replicaIndex = (replicaIndex + 1) % replicaPools.length;
  return pool;
}

async function query(sql, params, options = {}) {
  const isWrite = /^(INSERT|UPDATE|DELETE|CREATE|ALTER|DROP)/i.test(sql.trim());
  const pool = (isWrite || options.usePrimary) ? primaryPool : getReadPool();

  try {
    return await pool.query(sql, params);
  } catch (err) {
    // Retry on replica failure
    if (!isWrite && err.code === 'ECONNREFUSED') {
      console.warn('Replica failure, retrying on primary');
      return await primaryPool.query(sql, params);
    }
    throw err;
  }
}

module.exports = { query };
```

## Step 4: Backup Strategy

### PostgreSQL Backups

```bash
# 1. Physical backups (WAL archiving + base backup)

# Base backup (weekly)
pg_basebackup -h localhost -U postgres -D /backup/base_$(date +%Y%m%d) -Fp -Xs -P

# Continuous WAL archiving (postgresql.conf already configured)
# Archive to S3
archive_command = 'aws s3 cp %p s3://my-bucket/wal/%f'

# 2. Logical backups (pg_dump)

# Full database backup (daily)
pg_dump -h localhost -U postgres -Fc -f /backup/mydb_$(date +%Y%m%d).dump mydb

# Upload to S3
aws s3 cp /backup/mydb_$(date +%Y%m%d).dump s3://my-bucket/backups/

# 3. Point-in-time recovery (PITR) setup
# Restore base backup + replay WAL up to specific point in time

pg_basebackup -h primary -U replicator -D /restore/pgdata -Fp -Xs -P

# Create recovery.conf (PG 11 and below) or recovery.signal (PG 12+)
cat > /restore/pgdata/recovery.signal <<EOF
restore_command = 'aws s3 cp s3://my-bucket/wal/%f %p'
recovery_target_time = '2024-01-15 10:30:00'
EOF

# Start PostgreSQL in recovery mode
pg_ctl -D /restore/pgdata start
```

### MySQL Backups

```bash
# 1. Logical backup (mysqldump)
mysqldump -h localhost -u root -p \
    --single-transaction \
    --routines \
    --triggers \
    --events \
    --all-databases \
    --master-data=2 \
    > /backup/mysql_$(date +%Y%m%d).sql

# 2. Physical backup (Percona XtraBackup)
xtrabackup --backup \
    --target-dir=/backup/xtrabackup_$(date +%Y%m%d) \
    --user=root \
    --password=password

# 3. Incremental backup
xtrabackup --backup \
    --target-dir=/backup/xtrabackup_inc_$(date +%Y%m%d) \
    --incremental-basedir=/backup/xtrabackup_20240115 \
    --user=root \
    --password=password

# 4. Restore
xtrabackup --prepare --target-dir=/backup/xtrabackup_20240115
xtrabackup --copy-back --target-dir=/backup/xtrabackup_20240115
chown -R mysql:mysql /var/lib/mysql
systemctl start mysql
```

### Backup Automation (Cron)

```cron
# /etc/cron.d/database-backup

# Daily full backup at 2 AM
0 2 * * * postgres /usr/local/bin/backup-postgres.sh

# Hourly WAL archive check
0 * * * * postgres /usr/local/bin/check-wal-archive.sh

# Weekly base backup on Sunday at 3 AM
0 3 * * 0 postgres /usr/local/bin/base-backup-postgres.sh
```

## Step 5: Monitoring

### Key Metrics

```sql
-- PostgreSQL replication lag
SELECT
    client_addr,
    application_name,
    state,
    sync_state,
    pg_wal_lsn_diff(pg_current_wal_lsn(), sent_lsn) AS send_lag_bytes,
    pg_wal_lsn_diff(pg_current_wal_lsn(), write_lsn) AS write_lag_bytes,
    pg_wal_lsn_diff(pg_current_wal_lsn(), flush_lsn) AS flush_lag_bytes,
    pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS replay_lag_bytes,
    extract(epoch from (now() - pg_last_xact_replay_timestamp())) AS lag_seconds
FROM pg_stat_replication;

-- MySQL replication lag
SHOW SLAVE STATUS\G
-- Check: Seconds_Behind_Master

-- Connection pool stats (PgBouncer)
SHOW POOLS;
SHOW STATS;
```

### Alerting (Prometheus + Alertmanager)

```yaml
# prometheus-alerts.yml

groups:
  - name: database-ha
    rules:
      - alert: ReplicationLagHigh
        expr: pg_replication_lag_seconds > 60
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High replication lag detected"
          description: "Replication lag is {{ $value }}s"

      - alert: ReplicaDown
        expr: up{job="postgres-replica"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Replica is down"

      - alert: ConnectionPoolExhausted
        expr: pgbouncer_pools_cl_waiting > 10
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Connection pool has waiting clients"
```

## Step 6: Disaster Recovery

### DR Checklist

- [ ] Backups stored in separate geographic location
- [ ] Backup restoration tested quarterly
- [ ] RTO/RPO documented and tested
- [ ] Runbook for disaster scenarios
- [ ] On-call rotation defined
- [ ] Communication plan for incidents

### DR Testing

```bash
# Quarterly DR drill

# 1. Simulate primary failure
sudo systemctl stop postgresql  # On primary

# 2. Verify automatic failover (Patroni)
patronictl -c /etc/patroni/patroni.yml list
# Verify new primary is elected

# 3. Verify application connectivity
curl https://api.example.com/health

# 4. Bring old primary back as replica
sudo systemctl start postgresql
patronictl -c /etc/patroni/patroni.yml list

# 5. Document failover time (RTO)
# 6. Verify no data loss (RPO)
```

## Resources

- [PostgreSQL High Availability](https://www.postgresql.org/docs/current/high-availability.html)
- [Patroni Documentation](https://patroni.readthedocs.io/)
- [MySQL Replication](https://dev.mysql.com/doc/refman/8.0/en/replication.html)
- [PgBouncer Documentation](https://www.pgbouncer.org/)
- [ProxySQL Documentation](https://proxysql.com/documentation/)

---

**Template Version**: 1.0
**Last Updated**: 2025-11-19
