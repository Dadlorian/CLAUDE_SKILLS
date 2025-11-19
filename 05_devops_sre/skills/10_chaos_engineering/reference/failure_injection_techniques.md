# Failure Injection Techniques

## Overview

This reference provides a comprehensive catalog of failure injection techniques for chaos engineering experiments. Each technique includes the failure type, implementation methods, common use cases, and example scenarios.

## Failure Taxonomy

```
Failures
├── Infrastructure Failures
│   ├── Compute (CPU, Memory, Disk)
│   ├── Network (Latency, Loss, Partition)
│   └── Storage (I/O, Corruption)
├── Platform Failures
│   ├── Instance/Pod Failures
│   ├── Container Failures
│   └── Node/Host Failures
├── Application Failures
│   ├── Process Crashes
│   ├── Memory Leaks
│   └── Thread Exhaustion
├── Dependency Failures
│   ├── Service Unavailability
│   ├── API Errors
│   └── Database Failures
├── State Failures
│   ├── Configuration Errors
│   ├── Clock Skew
│   └── Certificate Expiration
└── Data Failures
    ├── Corruption
    ├── Loss
    └── Duplication
```

---

## 1. Resource Exhaustion Failures

### 1.1 CPU Stress

**Description**: Consume CPU resources to test application behavior under high CPU load.

**Scenarios to Test**:
- Application continues to function under CPU contention
- Auto-scaling triggers appropriately
- CPU-based health checks don't false-alarm
- Critical threads get CPU time despite load
- Monitoring and alerting work under load

**Implementation Methods**:

**Linux (stress-ng)**:
```bash
# Stress all CPU cores at 100%
stress-ng --cpu 0 --cpu-method all --timeout 60s

# Stress 4 cores at 80%
stress-ng --cpu 4 --cpu-load 80 --timeout 5m

# Stress with specific workload
stress-ng --cpu 2 --cpu-method fft --timeout 2m
```

**Gremlin**:
```bash
gremlin attack-cpu --cores 4 --percent 90 --length 300
```

**Kubernetes (Litmus)**:
```yaml
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosEngine
metadata:
  name: cpu-stress
spec:
  engineState: active
  appinfo:
    appns: default
    applabel: 'app=api-server'
    appkind: deployment
  chaosServiceAccount: litmus-admin
  experiments:
    - name: pod-cpu-hog
      spec:
        components:
          env:
            - name: CPU_CORES
              value: '2'
            - name: TOTAL_CHAOS_DURATION
              value: '60'
            - name: CPU_LOAD
              value: '100'
            - name: PODS_AFFECTED_PERC
              value: '50'
```

**Expected Behaviors**:
- Graceful degradation of non-critical features
- Request queuing or rate limiting
- Auto-scaling activation
- Circuit breakers to prevent cascade

**Anti-patterns**:
- Complete service unavailability
- No monitoring/alerting
- Cascading failures to dependencies

---

### 1.2 Memory Stress

**Description**: Exhaust available memory to test OOM handling and memory management.

**Scenarios to Test**:
- OOM killer doesn't crash critical processes
- Memory-based auto-scaling works
- Memory leaks are detected
- Swap usage is acceptable
- GC pressure handling

**Implementation Methods**:

**Linux (stress-ng)**:
```bash
# Allocate 2GB RAM
stress-ng --vm 1 --vm-bytes 2G --timeout 60s

# Allocate and touch memory pages
stress-ng --vm 4 --vm-bytes 512M --vm-method all --timeout 5m

# Create memory pressure with page faults
stress-ng --vm 2 --vm-bytes 1G --vm-populate --timeout 2m
```

**Gremlin**:
```bash
gremlin attack-memory --gb 4 --length 300
```

**Chaos Mesh**:
```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: StressChaos
metadata:
  name: memory-stress
  namespace: chaos-mesh
spec:
  mode: one
  selector:
    namespaces:
      - production
    labelSelectors:
      app: cache-service
  stressors:
    memory:
      workers: 4
      size: '2GB'
  duration: '2m'
```

**Expected Behaviors**:
- Memory-based eviction of caches
- Connection pool reduction
- GC activation and completion
- Pod eviction and rescheduling (Kubernetes)

---

### 1.3 Disk I/O Stress

**Description**: Saturate disk I/O to test database and storage-dependent services.

**Scenarios to Test**:
- Database performance under I/O contention
- Log writing doesn't block critical paths
- Disk space monitoring works
- Read/write timeouts are appropriate
- I/O priority settings are effective

**Implementation Methods**:

**Linux (ioping, fio)**:
```bash
# Saturate disk with reads
fio --name=randread --ioengine=libaio --iodepth=16 --rw=randread \
    --bs=4k --direct=1 --size=1G --numjobs=4 --runtime=60 --group_reporting

# Saturate with writes
fio --name=randwrite --ioengine=libaio --iodepth=16 --rw=randwrite \
    --bs=4k --direct=1 --size=1G --numjobs=4 --runtime=60 --fsync=1

# Mixed read/write
fio --name=randrw --ioengine=libaio --iodepth=16 --rw=randrw \
    --bs=4k --direct=1 --size=1G --numjobs=4 --runtime=60 --rwmixread=70
```

**Chaos Mesh (IOChaos)**:
```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: IOChaos
metadata:
  name: io-latency
  namespace: chaos-mesh
spec:
  action: latency
  mode: one
  selector:
    namespaces:
      - production
    labelSelectors:
      app: database
  volumePath: /var/lib/postgresql/data
  path: '/var/lib/postgresql/data/**/*'
  delay: '100ms'
  percent: 50
  duration: '5m'
```

**Expected Behaviors**:
- Query timeout handling
- Write-ahead log management
- Cache hit rate optimization
- I/O error handling

---

### 1.4 Disk Space Exhaustion

**Description**: Fill disk space to test handling of disk full conditions.

**Scenarios to Test**:
- Log rotation works properly
- Disk space alerts trigger
- Application handles write failures
- Database doesn't corrupt on disk full
- Cleanup jobs activate

**Implementation Methods**:

**Linux**:
```bash
# Fill disk to 95% capacity
df -h / | awk 'NR==2 {print $4}' | sed 's/G//' | \
  xargs -I {} dd if=/dev/zero of=/tmp/fillfile bs=1G count={}

# Fill specific directory
fallocate -l 10G /var/log/fillfile

# Fill with many small files
mkdir /tmp/diskfill && cd /tmp/diskfill
for i in {1..100000}; do echo "fill" > file$i; done
```

**Gremlin**:
```bash
gremlin attack-disk --workers 4 --size 10000 --length 300 --dir /var/log
```

**Expected Behaviors**:
- Graceful write failure handling
- Alert before reaching 100%
- Automatic cleanup activation
- Read operations continue working

---

## 2. Network Failures

### 2.1 Network Latency

**Description**: Introduce delays in network communication to test timeout handling.

**Scenarios to Test**:
- Timeouts are set appropriately
- User experience degrades gracefully
- Retry logic works correctly
- Circuit breakers activate
- Async operations handle delays

**Implementation Methods**:

**Linux (tc - traffic control)**:
```bash
# Add 100ms latency to all traffic
tc qdisc add dev eth0 root netem delay 100ms

# Add variable latency (100ms ± 20ms)
tc qdisc add dev eth0 root netem delay 100ms 20ms

# Add latency with correlation
tc qdisc add dev eth0 root netem delay 100ms 20ms 25%

# Add latency to specific destination
tc qdisc add dev eth0 root handle 1: prio
tc filter add dev eth0 parent 1:0 protocol ip prio 1 \
  u32 match ip dst 10.0.1.0/24 flowid 1:1
tc qdisc add dev eth0 parent 1:1 netem delay 200ms

# Remove latency
tc qdisc del dev eth0 root
```

**Gremlin**:
```bash
gremlin attack-latency --length 300 --delay 500 --target api.example.com
```

**Chaos Mesh**:
```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: network-delay
  namespace: chaos-mesh
spec:
  action: delay
  mode: all
  selector:
    namespaces:
      - production
    labelSelectors:
      app: frontend
  delay:
    latency: '200ms'
    correlation: '50'
    jitter: '50ms'
  duration: '5m'
  direction: to
  target:
    mode: all
    selector:
      namespaces:
        - production
      labelSelectors:
        app: backend
```

**Expected Behaviors**:
- Requests timeout appropriately (not too early, not too late)
- Retries with exponential backoff
- Circuit breaker opens after threshold
- User feedback shows loading state
- Async operations don't block

---

### 2.2 Packet Loss

**Description**: Drop packets to simulate unreliable network conditions.

**Scenarios to Test**:
- TCP retransmission works
- Application-level retries function
- Idempotency is maintained
- Duplicate detection works
- Health checks are resilient

**Implementation Methods**:

**Linux (tc)**:
```bash
# Drop 10% of packets
tc qdisc add dev eth0 root netem loss 10%

# Drop 10% with 25% correlation
tc qdisc add dev eth0 root netem loss 10% 25%

# Drop packets in bursts
tc qdisc add dev eth0 root netem loss gemodel 10% 50% 20% 80%
```

**Litmus**:
```yaml
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosEngine
metadata:
  name: network-loss
spec:
  engineState: active
  appinfo:
    appns: production
    applabel: 'app=api'
    appkind: deployment
  chaosServiceAccount: litmus-admin
  experiments:
    - name: pod-network-loss
      spec:
        components:
          env:
            - name: NETWORK_INTERFACE
              value: 'eth0'
            - name: NETWORK_PACKET_LOSS_PERCENTAGE
              value: '20'
            - name: TOTAL_CHAOS_DURATION
              value: '120'
            - name: TARGET_PODS
              value: 'api-*'
```

**Expected Behaviors**:
- Successful eventual delivery
- No duplicate processing
- Appropriate timeout values
- Monitoring shows packet loss

---

### 2.3 Network Partition (Split-Brain)

**Description**: Completely isolate network segments to test partition tolerance.

**Scenarios to Test**:
- Split-brain resolution in clustered systems
- Partition detection mechanisms
- Read/write behavior during partition
- Quorum-based decision making
- Partition healing after recovery

**Implementation Methods**:

**Linux (iptables)**:
```bash
# Block all traffic from specific IP
iptables -A INPUT -s 10.0.1.100 -j DROP
iptables -A OUTPUT -d 10.0.1.100 -j DROP

# Block specific port
iptables -A INPUT -p tcp --dport 5432 -j DROP

# Block subnet
iptables -A INPUT -s 10.0.1.0/24 -j DROP
iptables -A OUTPUT -d 10.0.1.0/24 -j DROP

# Remove rules
iptables -F
```

**Chaos Mesh**:
```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: partition
  namespace: chaos-mesh
spec:
  action: partition
  mode: all
  selector:
    namespaces:
      - production
    labelSelectors:
      app: database
      role: primary
  direction: both
  target:
    mode: all
    selector:
      namespaces:
        - production
      labelSelectors:
        app: database
        role: replica
  duration: '2m'
```

**Expected Behaviors**:
- Cluster maintains quorum
- Writes are rejected or queued
- Reads may serve stale data (if configured)
- Automatic leader election
- No data corruption

---

### 2.4 Bandwidth Limitation

**Description**: Limit network bandwidth to test behavior under constrained networks.

**Scenarios to Test**:
- Large payload handling
- Streaming service degradation
- File upload/download behavior
- Backpressure handling
- Queue buildup management

**Implementation Methods**:

**Linux (tc)**:
```bash
# Limit to 1Mbit
tc qdisc add dev eth0 root tbf rate 1mbit burst 32kbit latency 400ms

# Limit with HTB (Hierarchical Token Bucket)
tc qdisc add dev eth0 root handle 1: htb default 10
tc class add dev eth0 parent 1: classid 1:1 htb rate 10mbit
tc class add dev eth0 parent 1:1 classid 1:10 htb rate 1mbit ceil 10mbit
```

**Chaos Mesh**:
```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: bandwidth-limit
  namespace: chaos-mesh
spec:
  action: bandwidth
  mode: all
  selector:
    namespaces:
      - production
    labelSelectors:
      app: file-server
  bandwidth:
    rate: '1mbps'
    limit: 1000
    buffer: 10000
  duration: '5m'
```

---

### 2.5 DNS Failures

**Description**: Disrupt DNS resolution to test DNS caching and failure handling.

**Scenarios to Test**:
- DNS caching effectiveness
- DNS timeout handling
- Fallback DNS servers work
- Service discovery resilience
- Hard-coded IPs as fallback

**Implementation Methods**:

**Linux**:
```bash
# Block DNS queries
iptables -A OUTPUT -p udp --dport 53 -j DROP
iptables -A OUTPUT -p tcp --dport 53 -j DROP

# Return wrong DNS answers (using dnsmasq)
echo "address=/api.example.com/127.0.0.1" >> /etc/dnsmasq.conf
systemctl restart dnsmasq
```

**Chaos Mesh**:
```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: DNSChaos
metadata:
  name: dns-error
  namespace: chaos-mesh
spec:
  action: error
  mode: all
  selector:
    namespaces:
      - production
    labelSelectors:
      app: frontend
  patterns:
    - api.backend.svc.cluster.local
    - '*.example.com'
  duration: '3m'
```

---

## 3. Instance and Container Failures

### 3.1 Instance/Pod Termination

**Description**: Abruptly terminate instances or pods to test resilience and recovery.

**Scenarios to Test**:
- Service continues with fewer instances
- Load balancer updates quickly
- Stateful services handle termination
- Data is not lost
- Auto-scaling replaces instances

**Implementation Methods**:

**AWS EC2**:
```bash
# Terminate instance
aws ec2 terminate-instances --instance-ids i-1234567890abcdef0

# Stop instance (can be restarted)
aws ec2 stop-instances --instance-ids i-1234567890abcdef0
```

**Kubernetes**:
```bash
# Delete pod
kubectl delete pod api-server-abc123 -n production

# Delete pods by label
kubectl delete pods -l app=api-server -n production --grace-period=0 --force
```

**Litmus**:
```yaml
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosEngine
metadata:
  name: pod-delete
spec:
  engineState: active
  appinfo:
    appns: production
    applabel: 'app=api-server'
    appkind: deployment
  chaosServiceAccount: litmus-admin
  experiments:
    - name: pod-delete
      spec:
        components:
          env:
            - name: TOTAL_CHAOS_DURATION
              value: '300'
            - name: CHAOS_INTERVAL
              value: '30'
            - name: FORCE
              value: 'false'
```

**Expected Behaviors**:
- No dropped requests (or minimal)
- Quick replacement of terminated instances
- Stateful data preserved or recoverable
- Alerts for unexpected terminations

---

### 3.2 Container Kill

**Description**: Kill specific containers within a pod to test multi-container resilience.

**Scenarios to Test**:
- Sidecar container restart doesn't affect main container
- Init containers complete successfully after restart
- Shared volumes remain accessible
- Pod stays running with some containers down

**Implementation Methods**:

**Docker**:
```bash
# Kill container
docker kill <container-id>

# Stop container gracefully
docker stop <container-id>
```

**Kubernetes (Litmus)**:
```yaml
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosEngine
metadata:
  name: container-kill
spec:
  engineState: active
  appinfo:
    appns: production
    applabel: 'app=web-server'
    appkind: deployment
  chaosServiceAccount: litmus-admin
  experiments:
    - name: container-kill
      spec:
        components:
          env:
            - name: TARGET_CONTAINER
              value: 'sidecar-proxy'
            - name: TOTAL_CHAOS_DURATION
              value: '60'
            - name: CHAOS_INTERVAL
              value: '15'
            - name: SIGNAL
              value: 'SIGKILL'
```

---

### 3.3 Process Kill

**Description**: Kill specific processes to test process supervision and restart logic.

**Scenarios to Test**:
- Process managers restart processes
- Parent processes handle child death
- PID 1 behavior in containers
- Zombie process cleanup
- Signal handling

**Implementation Methods**:

**Linux**:
```bash
# Kill by PID
kill -9 <pid>

# Kill by name
pkill -9 nginx

# Kill all processes matching pattern
killall -9 java
```

**Gremlin**:
```bash
gremlin attack-process --process nginx --signal SIGKILL --length 60
```

**Litmus**:
```yaml
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosEngine
metadata:
  name: process-kill
spec:
  engineState: active
  appinfo:
    appns: production
    applabel: 'app=database'
    appkind: statefulset
  chaosServiceAccount: litmus-admin
  experiments:
    - name: pod-autoscaler
      spec:
        components:
          env:
            - name: PROCESS_NAME
              value: 'postgres'
            - name: TOTAL_CHAOS_DURATION
              value: '120'
            - name: CHAOS_INTERVAL
              value: '20'
```

---

## 4. Application-Level Failures

### 4.1 HTTP Error Injection

**Description**: Return HTTP error codes to test error handling in clients.

**Scenarios to Test**:
- 4xx error handling (client errors)
- 5xx error handling (server errors)
- Retry logic for transient errors
- Circuit breaker activation
- User-facing error messages

**Implementation Methods**:

**Nginx (testing backend)**:
```nginx
location /api {
    # Return 503 for 30% of requests
    if ($request_id ~* "[0-2]$") {
        return 503;
    }
    proxy_pass http://backend;
}
```

**Chaos Mesh**:
```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: HTTPChaos
metadata:
  name: http-abort
  namespace: chaos-mesh
spec:
  mode: all
  selector:
    namespaces:
      - production
    labelSelectors:
      app: api-gateway
  target: Request
  port: 8080
  path: '/api/v1/*'
  abort: true
  statusCode: 503
  duration: '5m'
```

**Expected Behaviors**:
- Retries for 5xx errors
- No retries for 4xx errors (except 429)
- Circuit breaker opens after threshold
- Proper error logging
- User-friendly error messages

---

### 4.2 Slow Response Injection

**Description**: Artificially slow down responses to test timeout handling.

**Scenarios to Test**:
- Client timeout configuration
- Async operation handling
- UI loading states
- Database connection pooling
- Thread pool exhaustion

**Implementation Methods**:

**Application code (middleware)**:
```python
# Python/Flask example
import time
import random

@app.before_request
def chaos_delay():
    if random.random() < 0.1:  # 10% of requests
        time.sleep(5)  # 5 second delay
```

**Chaos Mesh**:
```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: HTTPChaos
metadata:
  name: http-delay
  namespace: chaos-mesh
spec:
  mode: all
  selector:
    namespaces:
      - production
    labelSelectors:
      app: api
  target: Response
  port: 8080
  path: '/api/*'
  delay: '3s'
  duration: '5m'
```

---

### 4.3 Exception Injection

**Description**: Inject exceptions or errors in application code.

**Scenarios to Test**:
- Exception handling completeness
- Error propagation
- Transaction rollback
- Logging and monitoring
- Graceful degradation

**Implementation Methods**:

**Java (using fault injection library)**:
```java
import com.google.common.testing.FaultInjection;

public class UserService {
    @FaultInjection(type = "exception", rate = 0.05)
    public User getUser(String id) {
        // 5% chance of throwing exception
        return userRepository.findById(id);
    }
}
```

**Python (decorator-based)**:
```python
import random
from functools import wraps

def chaos_exception(rate=0.1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if random.random() < rate:
                raise Exception("Chaos: Random exception")
            return func(*args, **kwargs)
        return wrapper
    return decorator

@chaos_exception(rate=0.05)
def process_order(order_id):
    # Process order logic
    pass
```

---

## 5. State and Configuration Failures

### 5.1 Clock Skew (Time Travel)

**Description**: Modify system time to test time-dependent logic.

**Scenarios to Test**:
- Certificate expiration handling
- Token expiration
- Time-based caching
- Scheduled job execution
- Distributed system clock sync

**Implementation Methods**:

**Linux**:
```bash
# Set time forward by 1 day
date -s '+1 day'

# Set specific date/time
date -s '2024-12-31 23:59:00'

# Use libfaketime for specific process
LD_PRELOAD=/usr/lib/faketime/libfaketime.so.1 \
  FAKETIME='+1y' \
  ./myapp
```

**Gremlin**:
```bash
gremlin attack-time --offset 86400 --length 300  # +1 day
```

**Chaos Mesh**:
```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: TimeChaos
metadata:
  name: time-skew
  namespace: chaos-mesh
spec:
  mode: all
  selector:
    namespaces:
      - production
    labelSelectors:
      app: auth-service
  timeOffset: '24h'  # Move clock forward 24 hours
  duration: '10m'
```

**Expected Behaviors**:
- Graceful certificate renewal
- Token refresh mechanisms
- NTP re-sync after recovery
- Logging shows time anomaly

---

### 5.2 Configuration Corruption

**Description**: Modify or corrupt configuration to test validation and fallback.

**Scenarios to Test**:
- Configuration validation
- Fallback to defaults
- Hot reload handling
- Syntax error detection
- Version rollback

**Implementation Methods**:

**File-based config**:
```bash
# Corrupt JSON config
echo "invalid json{" > /etc/app/config.json

# Remove required field
jq 'del(.database.host)' config.json > config.json.tmp
mv config.json.tmp config.json

# Change to invalid value
sed -i 's/"port": 8080/"port": "invalid"/' config.json
```

**Kubernetes ConfigMap**:
```bash
# Corrupt ConfigMap
kubectl patch configmap app-config -n production \
  -p '{"data":{"database.url":"invalid://"}}'
```

**Expected Behaviors**:
- Application refuses to start with invalid config
- Validation errors are logged clearly
- Falls back to previous config version
- Alerts on config validation failures

---

### 5.3 Certificate Expiration

**Description**: Test SSL/TLS certificate expiration handling.

**Scenarios to Test**:
- Certificate validation
- Expiration warnings
- Automatic renewal
- Client connection behavior
- Monitoring and alerts

**Implementation Methods**:

**Chaos Mesh (Time Travel)**:
```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: TimeChaos
metadata:
  name: cert-expiration-test
  namespace: chaos-mesh
spec:
  mode: all
  selector:
    namespaces:
      - production
    labelSelectors:
      app: api-gateway
  timeOffset: '400d'  # Move forward past cert expiration
  duration: '5m'
```

**Manual**:
```bash
# Replace with expired certificate
cp /path/to/expired-cert.pem /etc/ssl/certs/app.pem
systemctl reload nginx
```

---

## 6. Data Layer Failures

### 6.1 Database Connection Failure

**Description**: Simulate database unavailability or connection failures.

**Scenarios to Test**:
- Connection pool exhaustion
- Retry logic
- Circuit breaker activation
- Read replica failover
- Queue-based eventual consistency

**Implementation Methods**:

**Network-based (block database port)**:
```bash
# Block PostgreSQL
iptables -A OUTPUT -p tcp --dport 5432 -j DROP

# Block specific database server
iptables -A OUTPUT -p tcp -d 10.0.1.100 --dport 5432 -j DROP
```

**AWS FIS**:
```json
{
  "actions": {
    "failover-db": {
      "actionId": "aws:rds:failover-db-cluster",
      "targets": {
        "Clusters": "db-cluster-prod"
      }
    }
  }
}
```

**Expected Behaviors**:
- Connection retry with backoff
- Circuit breaker opens
- Fallback to cache
- Queue writes for later
- Graceful degradation

---

### 6.2 Database Query Latency

**Description**: Slow down database queries to test timeout and performance.

**Scenarios to Test**:
- Query timeout handling
- Connection pool management
- Read/write splitting effectiveness
- Cache effectiveness
- Slow query detection

**Implementation Methods**:

**PostgreSQL (pg_sleep)**:
```sql
-- Create wrapper function that adds delay
CREATE OR REPLACE FUNCTION chaos_delay()
RETURNS void AS $$
BEGIN
  IF random() < 0.1 THEN  -- 10% of queries
    PERFORM pg_sleep(5);
  END IF;
END;
$$ LANGUAGE plpgsql;

-- Add to existing function
ALTER FUNCTION get_user(integer)
  SET search_path = public, chaos;
```

**Network latency (affects all DB traffic)**:
```bash
tc qdisc add dev eth0 root netem delay 500ms
```

---

### 6.3 Data Corruption

**Description**: Corrupt data to test validation and error handling.

**Scenarios to Test**:
- Data validation
- Schema enforcement
- Constraint violation handling
- Checksum verification
- Backup/restore procedures

**Implementation Methods**:

**File-based corruption**:
```bash
# Corrupt random bytes in file
dd if=/dev/urandom of=/data/database.db bs=1 count=100 seek=1000 conv=notrunc
```

**Database**:
```sql
-- Insert invalid data bypassing constraints
UPDATE users SET email = 'not-an-email' WHERE id = 123;

-- Violate foreign key (if not enforced)
INSERT INTO orders (user_id, product_id) VALUES (99999, 1);
```

---

## 7. Cloud Provider Failures

### 7.1 Availability Zone Failure

**Description**: Simulate entire AZ going down.

**Scenarios to Test**:
- Multi-AZ failover
- Cross-AZ load balancing
- Data replication
- Stateful service handling
- RTO/RPO validation

**Implementation Methods**:

**AWS FIS**:
```json
{
  "description": "Simulate AZ failure",
  "actions": {
    "stop-instances": {
      "actionId": "aws:ec2:stop-instances",
      "targets": {
        "Instances": "instances-in-az-1a"
      }
    }
  },
  "targets": {
    "instances-in-az-1a": {
      "resourceType": "aws:ec2:instance",
      "filters": [
        {
          "path": "Placement.AvailabilityZone",
          "values": ["us-east-1a"]
        }
      ],
      "selectionMode": "ALL"
    }
  }
}
```

**Gremlin (Blackhole to AZ)**:
```bash
gremlin attack-blackhole --hostname "*.us-east-1a.compute.amazonaws.com" --length 300
```

---

### 7.2 Region Failure

**Description**: Simulate entire region unavailability.

**Scenarios to Test**:
- Multi-region failover
- DNS-based routing
- Data replication lag
- Global load balancing
- Disaster recovery procedures

**Implementation Methods**:

**Route 53 health check**:
```bash
# Fail health check
aws route53 update-health-check \
  --health-check-id xxx \
  --inverted
```

**Network isolation**:
```bash
# Block all traffic to region CIDR
iptables -A OUTPUT -d 52.0.0.0/8 -j DROP  # Example AWS IP range
```

---

## 8. Advanced Failure Scenarios

### 8.1 Cascading Failures

**Description**: Trigger failures that cascade through system.

**Example Scenario**:
```
1. Slow database queries
   ↓
2. Connection pool exhaustion
   ↓
3. API timeout increases
   ↓
4. Circuit breaker opens
   ↓
5. Load shifts to healthy instances
   ↓
6. Healthy instances overload
   ↓
7. Complete service failure
```

**Implementation**: Combine multiple techniques progressively

---

### 8.2 Byzantine Failures

**Description**: Components give incorrect/inconsistent results rather than failing completely.

**Examples**:
- Return stale data
- Return data for wrong user
- Corrupt data in transit
- Partial writes
- Inconsistent reads

**Implementation Methods**:
```bash
# Return wrong data (via proxy)
# Modify response in transit
# Split-brain scenarios
# Clock skew causing ordering issues
```

---

## Failure Injection Best Practices

### 1. Start Small
- Begin with single-instance failures
- Short duration (30-60 seconds)
- Small blast radius (1-5%)
- Non-critical services first

### 2. Progressive Complexity
```
Week 1: Single pod delete
Week 2: Multiple pod deletes
Week 3: Network latency
Week 4: Combined pod delete + latency
Week 5: Database failover
Week 6: AZ failure
```

### 3. Always Have Abort Conditions
```yaml
stop_conditions:
  - error_rate > 1%
  - p99_latency > 5000ms
  - active_connections < 10
  - manual_intervention_required
```

### 4. Measure Everything
- Baseline metrics before chaos
- Continuous monitoring during chaos
- Delta analysis after chaos
- Long-term trend tracking

### 5. Document and Share
- Record all experiments
- Share results with team
- Track remediation items
- Build knowledge base

## Summary

Effective chaos engineering requires a comprehensive understanding of potential failure modes and appropriate injection techniques. This reference provides the foundation for building a robust chaos engineering practice that systematically tests and improves system resilience.

Remember:
- Failures are inevitable - test them proactively
- Start with low-risk experiments
- Automate and run continuously
- Learn and improve from every experiment
- Make resilience a shared responsibility
