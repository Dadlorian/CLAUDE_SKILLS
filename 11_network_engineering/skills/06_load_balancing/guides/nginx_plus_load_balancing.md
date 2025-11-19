# NGINX Plus Load Balancing Guide

## NGINX Plus vs NGINX OSS

### Feature Comparison
```
Feature                    NGINX OSS    NGINX Plus
License                    Free         Commercial
Basic Load Balancing       Yes          Yes
Advanced Health Checks     Limited      Advanced
Session Persistence        Limited      Advanced
Dynamic Reconfiguration    No           Yes
API                        No           Yes
Commercial Support         No           Yes
JWT Authentication         No           Yes
Key-Value Store           No           Yes
```

## Installation

### NGINX Plus Repository Setup

**Ubuntu/Debian**:
```bash
# Add NGINX Plus repository
sudo tee /etc/apt/sources.list.d/nginx-plus.list <<EOF
deb [signed-by=/usr/share/keyrings/nginx-archive-keyring.gpg] http://nginx.org/packages/ubuntu `lsb_release -cs` nginx-plus
deb-src [signed-by=/usr/share/keyrings/nginx-archive-keyring.gpg] http://nginx.org/packages/ubuntu `lsb_release -cs` nginx-plus
EOF

# Install key
curl https://nginx.org/keys/nginx_signing.key | gpg --dearmor | sudo tee /usr/share/keyrings/nginx-archive-keyring.gpg >/dev/null

# Install NGINX Plus
sudo apt-get update
sudo apt-get install nginx-plus
```

**CentOS/RHEL**:
```bash
# Add repository
sudo tee /etc/yum.repos.d/nginx-plus.repo <<EOF
[nginx-plus]
name=NGINX Plus Repository
baseurl=http://nginx.org/packages/centos/7/\$basearch/
enabled=1
gpgcheck=1
gpgkey=https://nginx.org/keys/nginx_signing.key
EOF

# Install
sudo yum install nginx-plus
```

### License Configuration
```
1. Obtain license file: nginx-repo.crt, nginx-repo.key
2. Place in /etc/ssl/nginx/:
   /etc/ssl/nginx/nginx-repo.crt
   /etc/ssl/nginx/nginx-repo.key
3. Restart repository manager:
   sudo systemctl restart apt-cacher-ng (Debian)
   sudo yum clean all (CentOS)
```

## Basic Configuration

### Simple Upstream
```nginx
upstream web_backend {
    server backend1.example.com weight=5;
    server backend2.example.com weight=3;
    server backend3.example.com weight=2;
}

server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://web_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### HTTPS Load Balancing
```nginx
upstream web_backend {
    server backend1.example.com;
    server backend2.example.com;
    server backend3.example.com;
}

server {
    listen 443 ssl http2;
    server_name example.com;

    ssl_certificate /etc/ssl/certs/example.com.crt;
    ssl_certificate_key /etc/ssl/private/example.com.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://web_backend;
    }
}
```

## Advanced Load Balancing Features

### Least Connections Method
```nginx
upstream web_backend {
    least_conn;

    server backend1.example.com;
    server backend2.example.com;
    server backend3.example.com;
}

server {
    location / {
        proxy_pass http://web_backend;
    }
}
```

### IP Hash (Sticky Sessions)
```nginx
upstream web_backend {
    ip_hash;

    server backend1.example.com;
    server backend2.example.com;
    server backend3.example.com;
}
```

### Hash Method (NGINX Plus)
```nginx
upstream web_backend {
    hash $request_uri consistent;  # Consistent hashing

    server backend1.example.com;
    server backend2.example.com;
    server backend3.example.com;
}
```

### Session Persistence (NGINX Plus)
```nginx
upstream web_backend {
    server backend1.example.com route=a;
    server backend2.example.com route=b;
    server backend3.example.com route=c;

    sticky cookie srv_id expires=1h domain=.example.com path=/ secure httponly;
}

server {
    location / {
        proxy_pass http://web_backend;
        proxy_cookie_path / "/";
    }
}
```

### Random Load Balancing
```nginx
upstream web_backend {
    random;  # Available in NGINX Plus

    server backend1.example.com;
    server backend2.example.com;
    server backend3.example.com;
}
```

## Health Checks (NGINX Plus)

### HTTP Health Checks
```nginx
upstream web_backend {
    server backend1.example.com max_fails=3 fail_timeout=30s;
    server backend2.example.com max_fails=3 fail_timeout=30s;
    server backend3.example.com max_fails=3 fail_timeout=30s;

    # NGINX Plus Advanced Health Checks
    zone backend_zone 64k;
    check interval=3000 rise=2 fall=5 timeout=1000 type=http;
    check_http_send "GET /health HTTP/1.0\r\n\r\n";
    check_http_expect_alive http_2xx http_3xx;
}

server {
    location /upstream_health {
        access_log off;
        default_type text/plain;
        upstream_health;  # Shows health status
    }
}
```

### TCP Health Checks
```nginx
upstream db_backend {
    zone db_zone 64k;

    server db1.example.com:3306;
    server db2.example.com:3306;

    check interval=5000 rise=1 fall=3 timeout=2000 type=tcp;
}
```

### Custom Health Check Interval
```nginx
upstream web_backend {
    zone backend_zone 64k;

    server backend1.example.com interval=5s rise=2 fall=3;
    server backend2.example.com interval=3s rise=2 fall=2;
    server backend3.example.com interval=10s rise=1 fall=5;

    check interval=3000 timeout=1000 type=http;
    check_http_send "GET /api/health HTTP/1.0\r\nHost: localhost\r\n\r\n";
    check_http_expect_alive http_2xx http_3xx;
}
```

## Dynamic Reconfiguration (NGINX Plus)

### API-Based Configuration
```bash
# Check current upstream config
curl http://localhost:8080/api/7/http/upstreams/web_backend

# Add new server
curl -X POST http://localhost:8080/api/7/http/upstreams/web_backend/servers \
  -d '{"server":"backend4.example.com:80"}'

# Modify server weight
curl -X PATCH http://localhost:8080/api/7/http/upstreams/web_backend/servers/0 \
  -d '{"weight":10}'

# Remove server
curl -X DELETE http://localhost:8080/api/7/http/upstreams/web_backend/servers/2
```

### Dashboard Configuration
```
Access NGINX Dashboard: https://your-nginx:8080/dashboard.html

Features:
- View upstream status
- Add/remove servers
- Adjust weights
- Monitor connections
- Real-time metrics
```

## SSL/TLS Configuration

### SSL Termination
```nginx
upstream web_backend {
    server backend1.example.com:80;  # Plain HTTP backend
    server backend2.example.com:80;
    server backend3.example.com:80;
}

server {
    listen 443 ssl http2;
    server_name example.com;

    ssl_certificate /etc/ssl/certs/example.com.crt;
    ssl_certificate_key /etc/ssl/private/example.com.key;

    # TLS Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    location / {
        proxy_pass http://web_backend;
    }
}
```

### SSL Bridging (Re-encryption)
```nginx
upstream web_backend_https {
    server backend1.example.com:443;
    server backend2.example.com:443;
    server backend3.example.com:443;
}

server {
    listen 443 ssl;
    server_name example.com;

    ssl_certificate /etc/ssl/certs/example.com.crt;
    ssl_certificate_key /etc/ssl/private/example.com.key;

    location / {
        proxy_pass https://web_backend_https;
        proxy_ssl_verify off;  # Or verify backend certificate
        proxy_ssl_protocols TLSv1.2 TLSv1.3;
    }
}
```

## Content-Based Routing

### Path-Based Routing
```nginx
upstream api_backend {
    server api1.example.com;
    server api2.example.com;
}

upstream web_backend {
    server web1.example.com;
    server web2.example.com;
}

upstream static_backend {
    server static1.example.com;
}

server {
    listen 80;
    server_name example.com;

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
upstream api_backend {
    server backend1.api.example.com;
}

upstream app_backend {
    server backend1.app.example.com;
}

server {
    listen 80;
    server_name api.example.com;
    proxy_pass http://api_backend;
}

server {
    listen 80;
    server_name app.example.com;
    proxy_pass http://app_backend;
}
```

### Header-Based Routing (NGINX Plus)
```nginx
upstream v2_backend {
    server backendv2.example.com;
}

upstream v1_backend {
    server backendv1.example.com;
}

server {
    location /api/ {
        if ($http_api_version = "v2") {
            proxy_pass http://v2_backend;
        }

        proxy_pass http://v1_backend;
    }
}
```

## Rate Limiting

### Request Rate Limiting
```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=web_limit:10m rate=100r/s;

upstream web_backend {
    server backend1.example.com;
    server backend2.example.com;
}

server {
    listen 80;

    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
        proxy_pass http://web_backend;
    }

    location / {
        limit_req zone=web_limit burst=100 nodelay;
        proxy_pass http://web_backend;
    }
}
```

## Monitoring and Troubleshooting

### Access Logs
```nginx
server {
    access_log /var/log/nginx/access.log main;

    # Custom format
    log_format detailed '$remote_addr - $remote_user [$time_local] '
                       '"$request" $status $body_bytes_sent '
                       '"$http_referer" "$http_user_agent" '
                       '$upstream_response_time';

    access_log /var/log/nginx/detailed.log detailed;
}
```

### Real-time Monitoring (NGINX Plus)
```
Dashboard URL: https://your-nginx:8080/dashboard.html

Metrics Shown:
- Request rate
- Error rates
- Upstream availability
- Response times
- Traffic distribution
- Connection counts
```

### Command-Line Debugging
```bash
# Test configuration
nginx -t

# View compiled version
nginx -v

# Show configuration
nginx -T

# Start NGINX
sudo systemctl start nginx

# Reload configuration
sudo systemctl reload nginx

# View status
sudo systemctl status nginx
```

## Performance Tuning

### Upstream Connection Pooling
```nginx
upstream web_backend {
    keepalive 32;
    keepalive_timeout 60s;
    keepalive_requests 100;

    server backend1.example.com;
    server backend2.example.com;
}

server {
    location / {
        proxy_pass http://web_backend;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }
}
```

### Buffer Configuration
```nginx
server {
    # Buffer settings for upstream
    proxy_buffering on;
    proxy_buffer_size 4k;
    proxy_buffers 8 4k;
    proxy_busy_buffers_size 8k;

    # Timeout settings
    proxy_connect_timeout 5s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;

    location / {
        proxy_pass http://web_backend;
    }
}
```

## Checklist: NGINX Plus Deployment

- [ ] NGINX Plus installed and licensed
- [ ] Configuration tested (nginx -t)
- [ ] Health checks configured and monitored
- [ ] SSL certificates installed and valid
- [ ] TLS versions configured (1.2+)
- [ ] Weak ciphers disabled
- [ ] Load balancing method selected appropriately
- [ ] Session persistence configured if needed
- [ ] Upstream backends verified healthy
- [ ] Logging configured
- [ ] Rate limiting configured
- [ ] Performance tested and baselined
- [ ] Failover tested
- [ ] Monitoring/alerting configured
- [ ] Documentation completed

---

**Last Updated**: 2025-11-19
**Version**: 2.0
