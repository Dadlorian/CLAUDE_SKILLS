# F5 BIG-IP Reference

## Overview
F5 BIG-IP is the industry-leading application delivery controller (ADC) platform, providing comprehensive L4-L7 load balancing, SSL/TLS offloading, DDoS protection, and application acceleration.

## BIG-IP Architecture

### Core Components

**Virtual Server (Virtual Server)**:
- Entry point for client connections
- Listens on IP:port combination
- Applies policies and profiles
- Routes to appropriate pool

**Pool**:
- Collection of backend servers
- Managed member list
- Health check configuration
- Load balancing algorithm selection

**Pool Member**:
- Individual backend server
- IP address and port
- Health status
- Connection limits

**Monitor (Health Check)**:
- Verifies pool member health
- Multiple monitor types
- Threshold configuration
- Action on status change

**iRule**:
- Custom traffic processing rules
- Written in TCL-like language
- Event-based execution
- Powerful customization

### System Organization

```
Virtual Server (Client Side)
    ↓
Client SSL Profile (if HTTPS)
    ↓
HTTP Profile
    ↓
Policy/iRule Processing
    ↓
Pool Selection
    ↓
Pool
    ├─ Member 1
    ├─ Member 2
    └─ Member 3
        ↓
    Server SSL Profile
        ↓
    Backend Server
```

## Virtual Server Configuration

### Basic Virtual Server
```
Name: vs_web_prod
IP Address: 203.0.113.1
Port: 443
Type: Standard (HTTP/HTTPS)
Profiles:
  - http
  - clientssl (for HTTPS)
  - serverssl (for backend SSL)
Default Pool: pool_web_backends
```

### Virtual Server Types
- **Standard**: Generic TCP/UDP/IP forwarding
- **Internal**: No client traffic (internal use)
- **Forwarding (IP)**: Forwards non-matching traffic
- **Performance (HTTP)**: Optimized for HTTP
- **Forwarding (L2)**: Layer 2 forwarding

## Pool Configuration

### Pool Settings
```yaml
Name: pool_web_backends
Load Balancing Method: Least Connections
Health Monitor:
  - HTTP GET /health
  - Interval: 5 seconds
  - Timeout: 3 seconds
Session Persistence: Cookie Insert
  - Cookie Name: f5_lb
  - Timeout: 1 hour
Members:
  - 192.168.1.10:80
  - 192.168.1.11:80
  - 192.168.1.12:80
```

### Load Balancing Methods
- Round Robin
- Least Connections
- Least Sessions
- Fastest (Response Time)
- Fewest Hops
- Weighted Round Robin
- Weighted Least Connections
- Dynamic Ratio
- Predictive Member Selection

## Monitor (Health Check) Configuration

### HTTP Monitor
```tcl
# F5 BIG-IP HTTP Monitor
set HTTP_VERSION "HTTP/1.1"
set HTTP_METHOD "GET"
set HTTP_PATH "/health-check"
set HTTP_EXPECTED_STATUS "200"

# Threshold configuration
set THRESHOLD_UP 2
set THRESHOLD_DOWN 3
set INTERVAL 5
set TIMEOUT 3
```

### Monitor Configuration
```yaml
Name: monitor_http_health
Type: HTTP
Protocol: HTTP
Port: 80
Method: GET
Path: /api/health
Receive String: "OK"
Send String: "GET /api/health HTTP/1.1\r\nHost: localhost\r\n\r\n"
Interval: 5 seconds
Timeout: 3 seconds
Up Count: 2
Down Count: 3
```

### Advanced Monitor
```yaml
Name: monitor_advanced
Type: HTTP
Method: POST
Path: /health-check
Send String: 'POST /health-check HTTP/1.1\r\nHost: localhost\r\nContent-Length: 0\r\n\r\n'
Receive String: '"status":"healthy"'
Username: monitoring
Password: [encrypted]
```

## SSL/TLS Configuration

### Client SSL Profile
```yaml
Name: clientssl_profile
Certificate: /Common/example.com.crt
Key: /Common/example.com.key
Chain: /Common/DigiCertCA.crt
Ciphers: "ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256"
Minimum Version: TLS 1.2
Maximum Version: TLS 1.3
Session Resumption: Enabled
SNI: Enabled (for multi-certificate)
```

### Server SSL Profile
```yaml
Name: serverssl_profile
Ciphers: "ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256"
Minimum Version: TLS 1.2
Certificate Verification:
  Mode: Require
  CA Certificate: /Common/backend-ca.crt
Renegotiation: Enabled
```

## iRule Examples

### Basic Request Routing
```tcl
when HTTP_REQUEST {
    # Route based on URI path
    if { [HTTP::uri] starts_with "/api" } {
        pool pool_api_backends
    } elseif { [HTTP::uri] starts_with "/static" } {
        pool pool_static_backends
    } else {
        pool pool_web_backends
    }
}
```

### Header Manipulation
```tcl
when HTTP_REQUEST {
    # Add X-Forwarded-For header
    HTTP::header insert X-Forwarded-For [IP::client_addr]
    HTTP::header insert X-Real-IP [IP::client_addr]

    # Remove sensitive headers
    HTTP::header remove X-Internal-Header
}
```

### Rate Limiting
```tcl
when HTTP_REQUEST {
    if { [info exists [IP::client_addr]] } {
        incr rate_limiter([IP::client_addr])
    } else {
        set rate_limiter([IP::client_addr]) 1
    }

    if { $rate_limiter([IP::client_addr]) > 100 } {
        HTTP::respond 429 content "Rate limit exceeded"
    }
}
```

## Policy Configuration

### Application Security Policy
```yaml
Name: web_app_security
Type: Application Security
Settings:
  - Cookie Security: Enabled
  - CSRF Protection: Enabled
  - Session Management: Enabled
  - Parameter Protection: Enabled
  - File Type Enforcement: Enabled
```

### Traffic Policy
```yaml
Name: traffic_management
Type: Traffic Policy
Rules:
  - Rule 1:
      Condition: HTTP::path starts_with "/api"
      Action: Forward to pool_api
  - Rule 2:
      Condition: HTTP::host equals "admin.example.com"
      Action: Forward to pool_admin
  - Rule 3:
      Condition: Default
      Action: Forward to pool_default
```

## Performance Tuning

### Connection Optimization
```yaml
Virtual Server Settings:
  - Connection Limit: 1000
  - TCP Idle Timeout: 300 seconds
  - HTTP Keep-Alive: Enabled
  - Keep-Alive Timeout: 60 seconds

Pool Settings:
  - Connection Limit per Member: 100
  - Connection Timeout: 5 seconds
  - Reuse Timeout: 60 seconds
```

### Compression Configuration
```yaml
HTTP Compression:
  - Enabled: Yes
  - Compression Level: Balanced
  - Content Types:
    - text/html
    - text/css
    - application/javascript
    - application/json
  - Minimum Size: 1024 bytes
```

### Caching Configuration
```yaml
RAM Cache:
  - Enabled: Yes
  - Maximum Size: 1GB
  - Cache Age: 3600 seconds
  - Include Content Types:
    - text/html
    - application/json
    - image/*
```

## Troubleshooting Commands

### Check Virtual Server Status
```bash
show ltm virtual vs_web_prod
show ltm virtual-address
show ltm virtual recursive
```

### Check Pool Status
```bash
show ltm pool pool_web_backends
show ltm pool pool_web_backends members
show ltm node
```

### Monitor Health
```bash
show ltm monitor http
show ltm pool pool_web_backends monitor
show event-processing
```

### Connection Statistics
```bash
show sys statistics ltm
show ltm pool pool_web_backends stats
show ltm virtual vs_web_prod stats
```

## Deployment Best Practices

1. **High Availability**: Deploy in HA pair (Active-Standby)
2. **Backup Configuration**: Regular backups of BIG-IP config
3. **SSL Certificate Management**:
   - Automated renewal process
   - Proper certificate chain
   - SNI for multi-certificate
4. **Monitoring**:
   - Alert on pool member status changes
   - Monitor CPU/memory usage
   - Track SSL session metrics
5. **Performance Baseline**:
   - Establish baseline metrics
   - Monitor for deviations
   - Capacity planning
6. **iRule Development**:
   - Test in staging first
   - Version control iRules
   - Performance test custom code
7. **Security Hardening**:
   - Disable unnecessary services
   - Use HTTPS for admin access
   - Implement role-based access
   - Enable audit logging

## TMSH Commands for Automation

### Create Virtual Server
```bash
create ltm virtual vs_new_app {
    ip-protocol tcp
    mask 255.255.255.255
    destination 203.0.113.10:443
    pool pool_app_backend
    profiles {
        http {}
        clientssl {
            context clientside
        }
    }
}
```

### Modify Pool Member
```bash
modify ltm pool pool_web_backends members {
    192.168.1.10:80 {
        priority-group 1
    }
}
```

### Save Configuration
```bash
save sys config
```

---

**Last Updated**: 2025-11-19
**Version**: 2.0
