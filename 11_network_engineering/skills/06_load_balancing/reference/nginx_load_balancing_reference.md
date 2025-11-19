# NGINX Load Balancing Reference

## Overview
NGINX is a high-performance web server and load balancer with powerful features for both HTTP and TCP-based application distribution.

## Basic Load Balancing

### Upstream Block Configuration
```nginx
upstream backend {
    # Default: Round Robin
    server backend1.example.com:80;
    server backend2.example.com:80;
    server backend3.example.com:80;
}

server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Server List with Weights
```nginx
upstream backend {
    # Weighted load balancing
    server backend1.example.com:80 weight=5;
    server backend2.example.com:80 weight=3;
    server backend3.example.com:80 weight=1;
}
```

### Server Backup
```nginx
upstream backend {
    server primary.example.com:80;
    server primary-backup.example.com:80 backup;
    server secondary.example.com:80 backup;
}
```

### Server Down State
```nginx
upstream backend {
    server backend1.example.com:80;
    server backend2.example.com:80 down;  # Disabled
    server backend3.example.com:80;
}
```

## Load Balancing Methods

### Round Robin (Default)
```nginx
upstream backend {
    server backend1.example.com:80;
    server backend2.example.com:80;
    server backend3.example.com:80;
}
```

**Distribution**: Sequential through each server

### Least Connections
```nginx
upstream backend {
    least_conn;

    server backend1.example.com:80;
    server backend2.example.com:80;
    server backend3.example.com:80;
}
```

**Characteristic**: Routes to server with fewest active connections

### IP Hash
```nginx
upstream backend {
    ip_hash;

    server backend1.example.com:80;
    server backend2.example.com:80;
    server backend3.example.com:80;
}
```

**Characteristic**:
- Client IP determines backend
- Ensures session affinity
- Stateless persistence

### Hash Method
```nginx
upstream backend {
    # Hash based on custom variable
    hash $request_uri consistent;

    server backend1.example.com:80;
    server backend2.example.com:80;
    server backend3.example.com:80;
}
```

**Hash Variables**:
- `$request_uri`: Request URL
- `$cookie_jsessionid`: Session cookie
- `$request_method`: HTTP method
- `$request_body`: Request body (careful with size)

### Random
```nginx
upstream backend {
    random;

    server backend1.example.com:80;
    server backend2.example.com:80;
    server backend3.example.com:80;
}
```

**Characteristic**: Randomly selects a backend for each request

## Health Checks

### Basic Health Check (Open Source NGINX)
**Configuration**:
```nginx
upstream backend {
    server backend1.example.com:80 max_fails=3 fail_timeout=30s;
    server backend2.example.com:80 max_fails=3 fail_timeout=30s;
    server backend3.example.com:80 max_fails=3 fail_timeout=30s;
}
```

**Parameters**:
- `max_fails`: Consecutive failures before marking down
- `fail_timeout`: Duration server is considered down

### Advanced Health Checks (NGINX Plus)
```nginx
# NGINX Plus only
upstream backend {
    server backend1.example.com:80;
    server backend2.example.com:80;
    server backend3.example.com:80;

    # Health check configuration
    zone backend 64k;
    check interval=3000 rise=2 fall=5 timeout=1000 type=http;
    check_http_send "GET /health HTTP/1.0\r\n\r\n";
    check_http_expect_alive http_2xx http_3xx;
}
```

**Parameters**:
- `interval`: Check frequency (milliseconds)
- `rise`: Consecutive passes to mark healthy
- `fall`: Consecutive failures to mark unhealthy
- `timeout`: Check timeout
- `type`: Health check type (http, tcp, etc.)

### Health Check Status Page (NGINX Plus)
```nginx
server {
    listen 8080;

    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # Status page
    location /upstream_health {
        access_log off;
        default_type text/plain;
        upstream_health;
    }
}
```

## Session Persistence

### Cookie-Based Persistence (NGINX Plus)
```nginx
upstream backend {
    server backend1.example.com:80;
    server backend2.example.com:80;
    server backend3.example.com:80;

    # Create sticky session cookie
    sticky cookie srv_id expires=1h domain=.example.com path=/ secure httponly;
}
```

### Route-Based Persistence (NGINX Plus)
```nginx
upstream backend {
    server backend1.example.com:80 route=a;
    server backend2.example.com:80 route=b;
    server backend3.example.com:80 route=c;

    sticky route $route_id expires=1h;
}
```

### Source IP Persistence
```nginx
upstream backend {
    ip_hash;  # Ensures same client goes to same backend
    server backend1.example.com:80;
    server backend2.example.com:80;
}
```

### Custom Hash Persistence
```nginx
upstream backend {
    hash $cookie_jsessionid consistent;  # Hash session ID

    server backend1.example.com:80;
    server backend2.example.com:80;
}
```

## Proxy Configuration

### Basic Proxy Pass
```nginx
location / {
    proxy_pass http://backend;
}
```

### Proxy Headers
```nginx
location / {
    proxy_pass http://backend;

    # Pass original host
    proxy_set_header Host $host;

    # Pass client IP
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

    # Pass protocol
    proxy_set_header X-Forwarded-Proto $scheme;

    # Pass port
    proxy_set_header X-Forwarded-Port $server_port;
}
```

### Timeout Configuration
```nginx
location / {
    proxy_pass http://backend;

    # Timeouts
    proxy_connect_timeout 5s;   # Connection timeout
    proxy_send_timeout 60s;     # Send timeout
    proxy_read_timeout 60s;     # Read timeout

    # Buffer settings
    proxy_buffering on;
    proxy_buffer_size 4k;
    proxy_buffers 8 4k;
    proxy_busy_buffers_size 8k;
}
```

## SSL/TLS Termination

### HTTP to HTTPS Redirect
```nginx
server {
    listen 80;
    server_name example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name example.com;

    ssl_certificate /etc/ssl/certs/example.com.crt;
    ssl_certificate_key /etc/ssl/private/example.com.key;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    location / {
        proxy_pass http://backend;
    }
}
```

### Multiple Certificates (SNI)
```nginx
server {
    listen 443 ssl;
    server_name example.com;

    ssl_certificate /etc/ssl/certs/example.com.crt;
    ssl_certificate_key /etc/ssl/private/example.com.key;

    # ... SSL configuration
}

server {
    listen 443 ssl;
    server_name api.example.com;

    ssl_certificate /etc/ssl/certs/api.example.com.crt;
    ssl_certificate_key /etc/ssl/private/api.example.com.key;

    # ... SSL configuration
}
```

### SSL Session Configuration
```nginx
server {
    listen 443 ssl;

    # SSL session cache
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Optimize SSL
    ssl_early_data on;
    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 8.8.8.8 8.8.4.4;
}
```

## Content-Based Routing

### Path-Based Routing
```nginx
upstream api_backend {
    server api1.example.com:80;
    server api2.example.com:80;
}

upstream static_backend {
    server static1.example.com:80;
}

server {
    listen 80;

    location /api/ {
        proxy_pass http://api_backend;
    }

    location /static/ {
        proxy_pass http://static_backend;
    }

    location / {
        proxy_pass http://web_backend;
    }
}
```

### Host-Based Routing
```nginx
upstream example_backend {
    server backend1.example.com:80;
}

upstream api_backend {
    server backend2.api.example.com:80;
}

server {
    listen 80;
    server_name example.com;
    proxy_pass http://example_backend;
}

server {
    listen 80;
    server_name api.example.com;
    proxy_pass http://api_backend;
}
```

### Query Parameter Routing
```nginx
upstream v1_backend {
    server backend1.example.com:80;
}

upstream v2_backend {
    server backend2.example.com:80;
}

server {
    listen 80;

    location / {
        if ($arg_api_version = "v2") {
            proxy_pass http://v2_backend;
        }

        proxy_pass http://v1_backend;
    }
}
```

## Load Balancer Settings

### Connection Limits
```nginx
upstream backend {
    # Max concurrent connections per backend
    server backend1.example.com:80 max_conns=100;
    server backend2.example.com:80 max_conns=100;

    # Keep-alive connections
    keepalive 32;
    keepalive_timeout 60s;
    keepalive_requests 100;
}
```

### Request Buffering
```nginx
location / {
    proxy_pass http://backend;

    # Buffer request body
    proxy_request_buffering on;

    # Buffer response
    proxy_buffering on;
    proxy_buffer_size 4k;
    proxy_buffers 8 4k;
}
```

### Cache Configuration
```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m;

server {
    location / {
        proxy_pass http://backend;
        proxy_cache my_cache;
        proxy_cache_valid 200 10m;
        proxy_cache_valid 404 1m;
        proxy_cache_use_stale error timeout invalid_header updating;
    }
}
```

## Troubleshooting

### Check NGINX Status
```bash
nginx -t                    # Test configuration
nginx -T                    # Dump configuration
ps aux | grep nginx        # Check running processes
netstat -tulpn | grep nginx # Check listening ports
```

### View Proxy Logs
```nginx
server {
    location / {
        proxy_pass http://backend;

        # Enable debug logging
        error_log /var/log/nginx/proxy_debug.log debug;
        access_log /var/log/nginx/proxy_access.log;
    }
}
```

### Common Issues

**502 Bad Gateway**: Backend unavailable
```
Solution:
  - Check backend health
  - Verify proxy_pass configuration
  - Check firewall/routing
```

**Connection Timeout**: Slow response
```
Solution:
  - Increase proxy_read_timeout
  - Check backend performance
  - Verify network latency
```

**High Response Times**: Buffering issue
```
Solution:
  - Adjust buffer settings
  - Check backend performance
  - Monitor buffer overflow
```

---

**Last Updated**: 2025-11-19
**Version**: 2.0
