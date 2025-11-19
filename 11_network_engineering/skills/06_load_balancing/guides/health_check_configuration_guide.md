# Health Check Configuration Guide

## Health Check Fundamentals

### Why Health Checks Matter
Health checks ensure load balancers only send traffic to healthy backend servers, preventing requests from being sent to failed or degraded servers.

**Without Health Checks**:
```
Backend Server 1: Down (no monitoring)
  → Still receives traffic
  → Client sees timeouts/errors
  → Poor user experience
```

**With Health Checks**:
```
Backend Server 1: Down
  → Health check fails
  → LB removes from rotation
  → Traffic redirected to Server 2
  → Client unaffected
```

## Health Check Methods Selection

### Decision Tree
```
What protocol does service use?

TCP/UDP Service (Database, Cache)?
  ├─ Generic TCP/UDP health check
  └─ Application-specific (optional)

HTTP/HTTPS Service (Web App)?
  ├─ HTTP GET /health (simple)
  ├─ HEAD request (bandwidth efficient)
  └─ POST (complex scenarios)

Special Service (DB, Redis)?
  ├─ Database-specific health query
  ├─ Service protocol check (PING, etc.)
  └─ Script-based check
```

## TCP Health Check Configuration

### Basic TCP Check
**Configuration**:
```yaml
Monitor Type: TCP
Port: 3306 (MySQL)
Timeout: 3 seconds
Interval: 5 seconds
Up Threshold: 2 consecutive passes
Down Threshold: 3 consecutive failures
```

**How It Works**:
```
1. LB attempts TCP connection to IP:port
2. If connection succeeds: Server marked healthy
3. If connection fails: Server marked unhealthy
4. Close connection (no data sent/received)

Timeline:
  00:00 - Check 1 fails (DB down)
  00:05 - Check 2 fails
  00:10 - Check 3 fails → Mark DOWN
  00:15 - Check 4 fails (still down)
  [DB recovers]
  00:20 - Check 5 passes
  00:25 - Check 6 passes → Mark UP
```

### TCP Connection Options
```yaml
Bind Local Port: 0 (any available)
Keepalive: Enabled
TCP Reset: On close

Advanced:
  TCP Timeout: 3 seconds
  TCP Fragment: Disabled
  TCP Window Size: Default
```

### Troubleshooting TCP Checks
```
Issue: All servers marked down

Diagnosis:
  1. Check network connectivity (ping backend)
  2. Verify port is correct (netstat -tulpn)
  3. Verify firewall allows LB → backend
  4. Check backend service status

Solution:
  - Fix network connectivity
  - Verify port binding
  - Open firewall rules
  - Restart service
```

## HTTP Health Check Configuration

### Simple HTTP Check
**Configuration**:
```yaml
Monitor Type: HTTP
Method: GET
Path: /health
Port: 80
Expected Status: 200
Timeout: 3 seconds
Interval: 5 seconds
Up Threshold: 2
Down Threshold: 3
```

**Request Sent**:
```
GET /health HTTP/1.1
Host: [backend_ip]
Connection: close
User-Agent: LBMonitor/1.0
```

**Response Evaluation**:
```
Response 200 OK → Healthy
Response 503 Service Unavailable → Unhealthy
Timeout/Connection Error → Unhealthy
```

### Advanced HTTP Checks

**POST with Payload**:
```yaml
Method: POST
Path: /health-check
Content-Type: application/json
Payload: |
  {
    "check_type": "full",
    "include_dependencies": true
  }
Expected Status: 200
Expected String: "status":"healthy"
```

**Custom Headers**:
```yaml
Method: GET
Path: /api/health
Headers:
  X-Check-Type: external
  Authorization: Bearer health_token_xyz
Expected Status: 200
Expected String: OK
```

**Response Content Validation**:
```yaml
Method: GET
Path: /health
Expected Status: 200
Expect String: All systems operational
Receive String: (what to expect in response body)
```

**HEAD Request** (bandwidth efficient):
```yaml
Method: HEAD
Path: /health
Expected Status: 200
Timeout: 2 seconds (faster since no body)
```

### HTTP Health Check Best Practices

1. **Create Lightweight Endpoint**
```
Don't use: Your production request path
  - Heavy database queries
  - Expensive computations
  - Large response body

Use: Dedicated /health endpoint
  - Simple status check
  - No dependencies
  - Minimal response body

Example Implementation:
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok' });
});
```

2. **Include Dependency Checks**
```
Basic health check:
  - Application is running

Better health check:
  - Application is running
  - Database connectivity OK
  - Cache connectivity OK
  - External service reachable

Implementation:
app.get('/health', async (req, res) => {
  try {
    await db.query('SELECT 1');
    await cache.ping();
    res.status(200).json({ status: 'healthy' });
  } catch (e) {
    res.status(503).json({ status: 'unhealthy', error: e.message });
  }
});
```

3. **Appropriate Response Codes**
```
200 OK: Application healthy
201 Created: OK for health check
204 No Content: OK (no body needed)
503 Service Unavailable: Unhealthy
5xx Server Error: Unhealthy
```

## Database Health Checks

### MySQL Health Check
**Configuration**:
```yaml
Monitor Type: MySQL
Port: 3306
Username: health_check_user
Password: ***
Database: (leave empty or use specific DB)
Query: SELECT 1
Timeout: 5 seconds
Interval: 10 seconds
Up Threshold: 2
Down Threshold: 3
```

**Authentication Setup**:
```sql
-- Create health check user with minimal privileges
CREATE USER 'health_check'@'%' IDENTIFIED BY 'secure_password';
GRANT SELECT ON *.* TO 'health_check'@'%';
FLUSH PRIVILEGES;
```

**What Gets Checked**:
1. Network connectivity to MySQL port
2. Authentication with provided credentials
3. Ability to execute query
4. Query returns result

### PostgreSQL Health Check
**Configuration**:
```yaml
Monitor Type: PostgreSQL
Port: 5432
Username: health_check_user
Password: ***
Database: postgres
Query: SELECT 1
Timeout: 5 seconds
Interval: 10 seconds
```

### Redis Health Check
**Configuration** (if supported):
```yaml
Monitor Type: Redis
Port: 6379
Command: PING
Expected Response: PONG
Timeout: 3 seconds
Interval: 5 seconds
```

**Alternative (TCP + Script)**:
```bash
redis-cli -h backend_ip -p 6379 PING
# If returns PONG, server is healthy
```

## Advanced Health Checks

### Script-Based Health Check
**Custom Script Approach**:
```bash
#!/bin/bash
# Health check script for custom application

APP_URL="http://localhost:8080/health"
TIMEOUT=3

# Make request
response=$(curl -s -w "\n%{http_code}" --max-time $TIMEOUT "$APP_URL" 2>/dev/null)
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

# Check response code
if [[ "$http_code" != "200" ]]; then
  echo "Unhealthy: HTTP $http_code"
  exit 1
fi

# Check response contains expected string
if [[ ! "$body" =~ "healthy" ]]; then
  echo "Unhealthy: Missing 'healthy' in response"
  exit 1
fi

# All checks passed
echo "Healthy"
exit 0
```

**Configuration**:
```yaml
Monitor Type: Custom Script
Script: /usr/local/bin/health_check.sh
Timeout: 5 seconds
Interval: 10 seconds
Success Exit Code: 0
Failure Exit Code: non-zero
```

### SNMP Health Check
**Monitor System Metrics**:
```yaml
Monitor Type: SNMP
SNMP Version: v3
IP: backend_server_ip
OID: 1.3.6.1.2.1.25.3.2.1.5.1 (CPU Load)
Threshold: < 80%
Timeout: 5 seconds
Interval: 30 seconds
```

### Multi-Level Health Checks

**Combine Multiple Checks**:
```yaml
Monitors:
  - Network Check: TCP port 80
  - Application Check: HTTP GET /health
  - Dependency Check: Database connectivity
  - Performance Check: Response time < 100ms

Decision Logic:
  All must pass: Server HEALTHY
  Network fails: Server DOWN (remove from rotation)
  App check fails: Server UNHEALTHY (degrade)
  Dependency fails: Server DEGRADED
  Performance slow: Server SLOW (might degrade)
```

## Health Check Tuning

### Interval and Timeout Selection

**High-Frequency Checks** (Fast failure detection):
```yaml
Interval: 2 seconds
Timeout: 1 second
Healthy Threshold: 2
Unhealthy Threshold: 2

Time to failure detection: 4-6 seconds
Check frequency impact: High
Recommended for: Critical applications
```

**Standard Checks** (Good balance):
```yaml
Interval: 5-10 seconds
Timeout: 3 seconds
Healthy Threshold: 2
Unhealthy Threshold: 3

Time to failure detection: 15-30 seconds
Check frequency impact: Medium
Recommended for: Most applications
```

**Low-Frequency Checks** (Bandwidth conservative):
```yaml
Interval: 30 seconds
Timeout: 5 seconds
Healthy Threshold: 1
Unhealthy Threshold: 2

Time to failure detection: 30-60 seconds
Check frequency impact: Low
Recommended for: Non-critical services
```

### Threshold Tuning

**Up Threshold** (Mark healthy after):
```
Default: 2 consecutive passes
Increase if: Frequent false negatives (temporary timeouts)
Decrease if: Need faster recovery (but beware false positives)
Typical range: 1-3
```

**Down Threshold** (Mark unhealthy after):
```
Default: 3 consecutive failures
Increase if: Temporary network glitches
Decrease if: Need faster failure detection
Typical range: 2-5
```

**Example Tuning**:
```
Original (too fast to fail):
  Down Threshold: 1
  Problem: Temporary network hiccup marks server down

Adjusted (more tolerant):
  Down Threshold: 3
  Benefit: Tolerates temporary network issues
  Tradeoff: Slower failure detection (15 vs 5 seconds)
```

## Monitoring Health Checks

### Metrics to Track
```
1. Check Success Rate
   - Percentage of successful checks
   - Alert if < 95%

2. Check Response Time
   - Average check response time
   - P95 check response time
   - Alert if > 2x baseline

3. Server State Changes
   - Number of DOWN → UP transitions
   - Number of UP → DOWN transitions
   - Alert on rapid transitions

4. Check Coverage
   - Percentage of backends being checked
   - Alert if any backend not checked
```

### Troubleshooting Health Checks

**Issue: Healthy servers marked DOWN**

Causes:
- Health check endpoint broken
- Temporary network issue
- Check too strict
- Firewall blocking checks

Solution:
1. Manually verify backend (curl, telnet)
2. Check health check endpoint directly
3. Verify network connectivity
4. Review firewall rules
5. Adjust thresholds if temporary issues

**Issue: DOWN servers marked HEALTHY**

Causes:
- Check not detecting real issues
- Application broken but port responds
- Health check bypassing real dependencies

Solution:
1. Add dependency checks (DB, cache, etc.)
2. Use application-level health endpoint
3. Include business logic in checks
4. Add performance thresholds

**Issue: Excessive health check traffic**

Causes:
- Check interval too frequent
- Too many health check monitors
- Large response body

Solution:
1. Increase interval (if acceptable)
2. Consolidate redundant checks
3. Use lightweight endpoint (no body)
4. Use HEAD instead of GET

## Health Check Security

### Protecting Health Checks
```
Scenario: Health check endpoint accessible to everyone
Risk:
  - Attackers know system is up
  - Potential denial of service
  - Information disclosure

Solution:
  - Restrict health check access to LB IPs only
  - Use authentication if possible
  - Don't expose sensitive info in response
```

### Implementation Example
```nginx
location /health {
  # Only allow from load balancers
  allow 203.0.113.1;   # LB 1
  allow 203.0.113.2;   # LB 2
  deny all;

  # Lightweight response
  access_log off;
  return 200 "OK";
  add_header Content-Type text/plain;
}
```

## Checklist: Health Check Configuration

- [ ] Correct monitor type selected (TCP/HTTP/DB)
- [ ] Correct port configured (80 for HTTP, 3306 for MySQL)
- [ ] Interval set appropriately (5-30 seconds typical)
- [ ] Timeout less than interval
- [ ] Health endpoint/query works correctly
- [ ] Expected response configured correctly
- [ ] Thresholds appropriate for application
- [ ] Firewall allows LB → backend checks
- [ ] Health endpoint lightweight and responsive
- [ ] Authentication configured if needed
- [ ] Monitoring/alerting on check failures
- [ ] Documentation of health check logic

---

**Last Updated**: 2025-11-19
**Version**: 2.0
