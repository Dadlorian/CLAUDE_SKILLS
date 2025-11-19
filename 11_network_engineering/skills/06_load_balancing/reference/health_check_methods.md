# Health Check Methods Reference

## Overview
Health checks ensure load balancers only direct traffic to healthy backend servers. Different health check methods provide varying levels of application awareness and reliability.

## Basic Health Check Methods

### TCP Health Check
**Description**: Verifies if a TCP port is open and accepting connections.

**How It Works**:
1. Load balancer attempts TCP connection to backend
2. If connection succeeds, server is marked healthy
3. If connection fails, server is marked unhealthy

**Configuration Example**:
```
Protocol: TCP
Port: 3306 (MySQL)
Timeout: 3 seconds
Interval: 5 seconds
```

**Pros**:
- Simple and fast
- Works for any TCP service
- Low overhead
- Universally supported

**Cons**:
- Doesn't verify application functionality
- False positives (port open ≠ working)
- Can't verify data accuracy

**Use Cases**:
- Database connection verification
- Generic service availability check
- Lightweight health check

### UDP Health Check
**Description**: Verifies if a UDP port is open and responsive.

**How It Works**:
1. Load balancer sends UDP packet to backend
2. Expects response from backend
3. Timeout indicates unhealthy state

**Configuration Example**:
```
Protocol: UDP
Port: 53 (DNS)
Timeout: 3 seconds
Interval: 5 seconds
```

**Challenges**:
- UDP is connectionless
- No guaranteed delivery
- Requires service-specific packets

**Use Cases**:
- DNS service health
- RADIUS service health
- Custom UDP-based services

## HTTP/HTTPS Health Checks

### Simple HTTP Health Check
**Description**: Sends HTTP request and verifies response code.

**How It Works**:
1. Load balancer sends GET request to specified URL
2. Checks HTTP response status code
3. Expected codes: 200, 201, 202, 204, 301, 302

**Configuration Example**:
```
Protocol: HTTP
Path: /health
Method: GET
Timeout: 3 seconds
Interval: 5 seconds
Expected Status: 200
```

**Example Request**:
```
GET /health HTTP/1.1
Host: backend.example.com
Connection: close
```

**Pros**:
- Application-aware
- Can verify specific endpoints
- Supports custom logic
- Standard HTTP protocol

**Cons**:
- Requires HTTP service
- Higher overhead than TCP
- Depends on HTTP implementation

### HTTPS Health Check
**Description**: HTTP health check over SSL/TLS connection.

**Configuration Example**:
```
Protocol: HTTPS
Path: /api/health
Method: GET
Timeout: 3 seconds
Interval: 5 seconds
Expected Status: 200
Verify SSL Certificate: true
```

**Special Considerations**:
- SSL handshake overhead
- Certificate validation
- TLS version compatibility
- Cipher suite support

### HEAD Health Check
**Description**: Sends HEAD request instead of GET (no response body).

**Advantages**:
- Lower bandwidth usage
- Faster response
- Same response headers as GET
- Better for high-frequency checks

**Configuration Example**:
```
Protocol: HTTP
Method: HEAD
Path: /health
Interval: 2 seconds
```

### POST Health Check
**Description**: Sends POST request with optional payload.

**Use Cases**:
- Complex health verification
- Application state validation
- Custom health endpoints

**Configuration Example**:
```
Protocol: HTTP
Method: POST
Path: /health-check
Payload: {"check_level": "full"}
Expected Status: 200
```

## Application-Level Health Checks

### Scripted Health Check
**Description**: Executes custom script on backend to verify health.

**How It Works**:
1. Load balancer executes script via SSH or agent
2. Script verifies application state
3. Exit code determines health (0 = healthy)

**Example Script**:
```bash
#!/bin/bash
# Check if MySQL is responding
mysql -h localhost -u root -p'password' -e "SELECT 1" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "MySQL is healthy"
    exit 0
else
    echo "MySQL is unhealthy"
    exit 1
fi
```

**Pros**:
- Highly customizable
- Can check application logic
- Verify database connectivity
- Check file system

**Cons**:
- Requires agent/SSH access
- Higher overhead
- More complex to implement

### Database Health Check
**Description**: Verifies database connectivity and responsiveness.

**Supported Databases**:
- MySQL/MariaDB
- PostgreSQL
- MSSQL
- Oracle
- MongoDB

**Configuration Example** (MySQL):
```
Protocol: MySQL
Port: 3306
Username: health_check
Password: ****
Database: information_schema
Query: SELECT 1
Timeout: 3 seconds
```

**What's Checked**:
- Network connectivity
- Authentication
- Query execution
- Response time

### SNMP Health Check
**Description**: Uses SNMP to query system health metrics.

**Metrics Checked**:
- CPU utilization
- Memory usage
- Disk space
- Network interfaces
- Custom OIDs

**Configuration Example**:
```
Protocol: SNMP
Version: SNMPv3
OID: 1.3.6.1.2.1.25.3.2.1.5.1 (CPU Load)
Threshold: CPU < 80%
Timeout: 3 seconds
```

### Custom Application Protocol
**Description**: Application-specific protocol health verification.

**Examples**:
- **Redis**: PING command
- **Memcached**: STATS command
- **Rabbitmq**: AMQP connection
- **Elasticsearch**: GET /_cluster/health

**Redis Example**:
```
Protocol: Redis
Port: 6379
Command: PING
Expected Response: +PONG
```

## Advanced Health Check Concepts

### Health Check Frequency
**Interval**: Time between health checks
- Typical: 5-30 seconds
- High-frequency: 1-2 seconds
- Low-frequency: 60+ seconds

**Timeout**: Maximum wait for health check response
- Typical: 3-5 seconds
- Short: 1 second
- Long: 10+ seconds

### Health Status Transitions

#### Marked Down (After Failures)
**Configuration**:
```
Unhealthy Threshold: 3
Interval: 5 seconds
```
- Server needs 3 consecutive failed checks to mark down
- Takes 15 seconds minimum
- No traffic directed to server

#### Marked Up (After Success)
**Configuration**:
```
Healthy Threshold: 2
Interval: 5 seconds
```
- Server needs 2 consecutive successful checks to mark up
- Takes 10 seconds minimum
- Traffic gradually restored or immediately

### Health Check Aggregation
**Multiple Health Checks**:
```
Primary Health Check: HTTP GET /health
Secondary Health Check: TCP port 3306
Additional Check: CPU < 85%

Status Logic:
- All must pass for healthy status
- Any failure marks unhealthy
```

## Performance Considerations

### Load Balancer Resource Usage

| Method | CPU | Memory | Network | Latency |
|--------|-----|--------|---------|---------|
| TCP | Very Low | Low | Low | <10ms |
| HTTP | Low | Low | Medium | 10-50ms |
| HTTPS | Medium | Low | Medium | 50-200ms |
| Script | High | Medium | Medium | 100-1000ms |
| SNMP | Low | Low | Low | 20-100ms |
| DB Query | High | Medium | Low | 50-500ms |

### Optimal Health Check Strategies

**High-Frequency Scenarios** (Fast failure detection):
```
Interval: 2 seconds
Timeout: 1 second
Healthy Threshold: 2
Unhealthy Threshold: 2
Method: HTTP HEAD /health
```

**Standard Scenarios**:
```
Interval: 5 seconds
Timeout: 3 seconds
Healthy Threshold: 2
Unhealthy Threshold: 3
Method: HTTP GET /health
```

**Low-Frequency Scenarios** (Bandwidth sensitive):
```
Interval: 30 seconds
Timeout: 5 seconds
Healthy Threshold: 1
Unhealthy Threshold: 2
Method: TCP check only
```

## Health Check Response Codes

### HTTP Status Codes
| Code | Meaning | Action |
|------|---------|--------|
| 2xx | Success | Mark healthy |
| 3xx | Redirect | Mark healthy (follow if configured) |
| 4xx | Client Error | Mark unhealthy |
| 5xx | Server Error | Mark unhealthy |
| Timeout | No response | Mark unhealthy |

### Custom Status Mapping
```
200: Healthy
201: Healthy (Created)
202: Healthy (Accepted)
204: Healthy (No Content)
307: Maintenance (Temp unavailable)
503: Unhealthy (Service unavailable)
Timeout: Unhealthy
```

## Health Check Best Practices

1. **Use Application-Aware Health Checks**
   - Generic TCP checks miss application issues
   - Include business logic validation when possible

2. **Dedicated Health Endpoints**
   - Create lightweight health check endpoints
   - Don't use production endpoints
   - Return minimal response body

3. **Appropriate Frequency**
   - Balance between detection speed and overhead
   - Most scenarios: 5-10 second intervals
   - Critical applications: 2-5 second intervals

4. **Health Check Timeout**
   - Set slightly longer than expected response time
   - Account for network latency
   - Avoid false negatives

5. **Multiple Health Checks**
   - Combine different check types
   - Prevent false positives
   - Comprehensive health validation

6. **Disable During Maintenance**
   - Prevent false health check failures
   - Explicitly mark server as disabled
   - Clear traffic before maintenance

7. **Monitor Health Check Metrics**
   - Track false positive/negative rates
   - Alert on unusual patterns
   - Adjust thresholds as needed

8. **Health Check Security**
   - Authenticate health check requests if possible
   - Don't expose sensitive data
   - Rate limit health check endpoints

---

**Last Updated**: 2025-11-19
**Version**: 2.0
