# HAProxy Reference

## Overview
HAProxy is a free, open-source load balancer and proxy server supporting TCP and HTTP-based applications, known for high performance and reliability.

## HAProxy Architecture

### Core Components

**Frontend**:
- Listens for incoming connections
- Accepts client requests
- Applies rules and ACLs
- Forwards to backends

**Backend**:
- Pool of backend servers
- Health checking
- Load balancing algorithm
- Session persistence

**ACL (Access Control List)**:
- Condition evaluation
- Request matching
- Rule-based routing

**Bind**:
- Listen address and port
- Protocol configuration
- SSL/TLS settings

**Server**:
- Individual backend server
- Health status
- Connection parameters

## Frontend Configuration

### Basic Frontend
```
frontend http_in
    # Listen on all interfaces, port 80
    bind *:80

    # Default backend (fallback)
    default_backend backend_web

    # Accept both HTTP/1.0 and HTTP/1.1
    mode http

    # Timeout settings
    timeout client 50000
```

### HTTPS Frontend with SSL
```
frontend https_in
    # Listen on port 443 with SSL
    bind *:443 ssl crt /etc/ssl/certs/example.com.pem

    # SNI support for multiple certificates
    bind *:443 ssl crt /etc/ssl/certs/cert1.pem crt /etc/ssl/certs/cert2.pem

    # TLS Version control
    ssl-default-bind-options ssl-min-ver TLSv1.2

    # Cipher suite
    ssl-default-bind-ciphers ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256

    # Default backend
    default_backend backend_web
```

### TCP Frontend
```
frontend tcp_proxy
    # TCP mode (not HTTP)
    mode tcp

    # Listen on port 3306 (MySQL)
    bind *:3306

    # Default backend
    default_backend backend_mysql

    # Timeout for TCP
    timeout client 30000
```

## Backend Configuration

### Basic Backend
```
backend backend_web
    # HTTP mode
    mode http

    # Load balancing algorithm
    balance roundrobin

    # Health check
    option httpchk GET /health

    # Timeout settings
    timeout server 50000
    timeout connect 5000

    # Backend servers (pool members)
    server web1 192.168.1.10:80 check
    server web2 192.168.1.11:80 check
    server web3 192.168.1.12:80 check inter 5000 rise 2 fall 3
```

### Backend with Session Persistence
```
backend backend_web_sticky
    mode http
    balance roundrobin

    # Cookie-based session persistence
    cookie JSESSIONID insert indirect nocache

    # Health check
    option httpchk GET /health

    # Servers with cookie settings
    server web1 192.168.1.10:80 check cookie web1
    server web2 192.168.1.11:80 check cookie web2
    server web3 192.168.1.12:80 check cookie web3
```

### TCP Backend
```
backend backend_mysql
    mode tcp
    balance leastconn

    # TCP health check
    option tcp-check
    tcp-check connect port 3306

    # Timeout for server
    timeout server 30000

    # MySQL servers
    server mysql1 192.168.1.20:3306 check
    server mysql2 192.168.1.21:3306 check backup
```

## Load Balancing Algorithms

### Round Robin (Default)
```
backend web_rr
    balance roundrobin
    server web1 192.168.1.10:80
    server web2 192.168.1.11:80
    server web3 192.168.1.12:80
```

### Least Connections
```
backend web_leastconn
    balance leastconn
    server web1 192.168.1.10:80
    server web2 192.168.1.11:80
    server web3 192.168.1.12:80
```

### Source IP Hash
```
backend web_source
    balance source
    server web1 192.168.1.10:80
    server web2 192.168.1.11:80
    server web3 192.168.1.12:80
```

### Weighted Round Robin
```
backend web_weighted
    balance roundrobin
    server web1 192.168.1.10:80 weight 3
    server web2 192.168.1.11:80 weight 2
    server web3 192.168.1.12:80 weight 1
```

### URI Hash
```
backend web_uri
    balance uri
    server web1 192.168.1.10:80
    server web2 192.168.1.11:80
    server web3 192.168.1.12:80
```

## ACL and Routing Rules

### Basic ACL
```
frontend http_in
    bind *:80

    # Define ACLs
    acl is_api path_beg /api
    acl is_static path_beg /static
    acl is_admin hdr_beg(host) -i admin.

    # Use ACLs
    use_backend backend_api if is_api
    use_backend backend_static if is_static
    use_backend backend_admin if is_admin
    default_backend backend_web
```

### Advanced ACL Conditions
```
# Request method
acl is_post method POST
acl is_get method GET

# Host header
acl is_example_com hdr(host) -i example.com
acl is_subdomain hdr_beg(host) -i api.

# Source IP
acl is_internal src 192.168.0.0/16
acl is_trusted_ip src 203.0.113.1

# Port
acl is_https dst_port 443

# Combined ACL
acl is_api_post path_beg /api AND method POST
```

### Request Manipulation
```
frontend http_in
    bind *:80

    # Add headers
    http-request add-header X-Forwarded-For %[src]
    http-request add-header X-Real-IP %[src]
    http-request add-header X-Forwarded-Proto http

    # Remove headers
    http-request del-header X-Internal-Auth

    # Set custom headers
    http-request set-header X-Via haproxy
```

## Health Checking

### HTTP Health Check
```
backend web_backend
    mode http
    option httpchk GET /health HTTP/1.1
    option httpchk GET /health HTTP/1.1\r\nHost:\ localhost

    # Advanced health check
    http-check expect status 200

    # Server with health check parameters
    server web1 192.168.1.10:80 check inter 5000 rise 2 fall 3
```

### TCP Health Check
```
backend db_backend
    mode tcp
    option tcp-check
    tcp-check connect port 3306

    server db1 192.168.1.20:3306 check inter 5000
```

### Custom Health Check with Expect
```
backend app_backend
    mode http
    option httpchk GET /api/health
    http-check expect string "healthy"

    server app1 192.168.1.30:80 check
```

## SSL/TLS Configuration

### SSL Termination
```
frontend https_in
    bind *:443 ssl crt /etc/ssl/certs/example.com.pem

    # Force HTTPS redirect
    http-request redirect scheme https code 301 if !{ ssl_fc }

    # SSL session parameters
    tune ssl default-dh-param 2048

    # Backend using HTTP
    default_backend backend_web_http
```

### SSL Bridging (Re-encryption)
```
frontend https_in
    bind *:443 ssl crt /etc/ssl/certs/example.com.pem

    # Backend with HTTPS
    default_backend backend_web_https

backend backend_web_https
    mode http
    balance roundrobin

    # Use HTTPS to backend
    server web1 192.168.1.10:443 ssl verify none
    server web2 192.168.1.11:443 ssl verify none
```

### Multiple Certificates (SNI)
```
frontend https_in
    bind *:443 ssl \
        crt /etc/ssl/certs/example.com.pem \
        crt /etc/ssl/certs/example.org.pem \
        crt /etc/ssl/certs/test.example.com.pem

    # SNI-based routing
    acl sni_example ssl_fc_sni -i example.com
    acl sni_org ssl_fc_sni -i example.org

    use_backend backend_example if sni_example
    use_backend backend_org if sni_org
    default_backend backend_default
```

## Session Persistence

### Cookie Insert
```
backend sticky_web
    balance roundrobin
    cookie HAPROXY_SESSIONID insert indirect nocache

    server web1 192.168.1.10:80 check cookie web1
    server web2 192.168.1.11:80 check cookie web2
```

### Source IP Persistence
```
backend sticky_db
    balance source
    server db1 192.168.1.20:3306 check
    server db2 192.168.1.21:3306 check backup
```

## Global Configuration

### Global Settings
```
global
    # Logging
    log 127.0.0.1 local0 notice
    log 127.0.0.1 local0 info

    # Daemon mode
    daemon

    # Max connections
    maxconn 4096

    # User and group
    user haproxy
    group haproxy

    # Process management
    pidfile /var/run/haproxy.pid

    # SSL defaults
    tune ssl default-dh-param 2048
    ssl-default-bind-ciphers ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256
    ssl-default-bind-options ssl-min-ver TLSv1.2
```

### Defaults Section
```
defaults
    log     global
    mode    http

    # Timeouts
    timeout connect 5000
    timeout client  50000
    timeout server  50000

    # Error files
    errorfile 400 /etc/haproxy/errors/400.http
    errorfile 403 /etc/haproxy/errors/403.http
    errorfile 408 /etc/haproxy/errors/408.http
    errorfile 500 /etc/haproxy/errors/500.http
```

## Troubleshooting

### Check Configuration Syntax
```bash
haproxy -c -f /etc/haproxy/haproxy.cfg
```

### View Stats Page
```
frontend stats_in
    bind *:8404
    stats enable
    stats uri /stats
    stats refresh 30s
    stats admin if TRUE
```

### Enable Debug Logging
```
global
    log 127.0.0.1 local0 debug
```

### Common Issues

**502 Bad Gateway**: Backend connection failed
```
Solution: Check backend server health
  - Verify health check: show table (stats page)
  - Verify backend connectivity: telnet backend:port
  - Check firewall rules
```

**Connection Timeout**: Slow or no response
```
Solution: Increase timeout
  timeout server 50000 → timeout server 100000
```

**SSL Handshake Failed**: Certificate or TLS issue
```
Solution: Verify certificate
  - Check cert: openssl x509 -in cert.pem -text
  - Check TLS version: openssl s_client -tls1_2 -connect host:443
```

## Performance Tuning

### Connection Limits
```
global
    maxconn 100000

defaults
    maxconn 2000

frontend http_in
    bind *:80 maxconn 50000
```

### TCP Tuning
```
global
    tune.bufsize 16384
    tune.maxconn 100000
    tune.tcp.maxconn 100000
    tune.ssl.cachesize 1000000
```

### Keep-Alive
```
defaults
    option http-keep-alive
    timeout http-keep-alive 1000
```

---

**Last Updated**: 2025-11-19
**Version**: 2.0
