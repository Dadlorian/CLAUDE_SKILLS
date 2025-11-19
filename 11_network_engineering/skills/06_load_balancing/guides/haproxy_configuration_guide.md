# HAProxy Configuration Guide

## Installation and Setup

### Linux Installation

**Ubuntu/Debian**:
```bash
sudo apt-get update
sudo apt-get install haproxy

# Verify installation
haproxy -v
```

**CentOS/RHEL**:
```bash
sudo yum install haproxy

# Enable service
sudo systemctl enable haproxy
sudo systemctl start haproxy
```

**From Source** (Latest):
```bash
# Download latest source
cd /tmp
wget http://www.haproxy.org/download/[version]/src/haproxy-[version].tar.gz
tar xzf haproxy-[version].tar.gz
cd haproxy-[version]

# Build
make
sudo make install

# Install systemd service
sudo cp ./contrib/systemd/haproxy.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start haproxy
```

### Configuration File Location
```
Primary: /etc/haproxy/haproxy.cfg
Verify: haproxy -c -f /etc/haproxy/haproxy.cfg
Reload: systemctl reload haproxy
```

## Basic Configuration Structure

### Configuration Template
```
#-----------
# Global
#-----------
global
    log 127.0.0.1 local0 notice
    user haproxy
    group haproxy
    daemon
    maxconn 4096

#-----------
# Defaults
#-----------
defaults
    log     global
    mode    http
    timeout connect 5000
    timeout client  50000
    timeout server  50000
    errorfile 400 /etc/haproxy/errors/400.http
    errorfile 500 /etc/haproxy/errors/500.http

#-----------
# Frontend
#-----------
frontend http_in
    bind *:80
    default_backend web_backend

frontend https_in
    bind *:443 ssl crt /etc/ssl/certs/example.com.pem
    default_backend web_backend

#-----------
# Backend
#-----------
backend web_backend
    mode http
    balance roundrobin
    option httpchk GET /health

    server web1 192.168.1.10:80 check
    server web2 192.168.1.11:80 check
    server web3 192.168.1.12:80 check
```

## Frontend Configuration

### HTTP Frontend
```
frontend http_in
    # Bind to address and port
    bind 0.0.0.0:80

    # Default backend
    default_backend web_backend

    # HTTP mode
    mode http

    # Client timeout
    timeout client 50000

    # Optional: Add headers
    http-request add-header X-Forwarded-For %[src]
    http-request add-header X-Real-IP %[src]
```

### HTTPS Frontend with SSL

**Basic HTTPS**:
```
frontend https_in
    bind 0.0.0.0:443 ssl crt /etc/ssl/certs/example.com.pem

    mode http
    timeout client 50000

    # Force HTTPS redirect (optional)
    http-request redirect scheme https code 301 if !{ ssl_fc }

    default_backend web_backend
```

**Multiple Certificates (SNI)**:
```
frontend https_in
    # Multiple certificate files
    bind 0.0.0.0:443 ssl \
        crt /etc/ssl/certs/example.com.pem \
        crt /etc/ssl/certs/example.org.pem \
        crt /etc/ssl/certs/api.example.com.pem

    default_backend web_backend
```

### Request Processing

**Add Headers**:
```
frontend http_in
    bind *:80

    # Add original client IP
    http-request add-header X-Forwarded-For %[src]

    # Add real IP
    http-request add-header X-Real-IP %[src]

    # Add protocol
    http-request add-header X-Forwarded-Proto %[scheme]

    # Add port
    http-request add-header X-Forwarded-Port %[dst_port]

    default_backend web_backend
```

**Content-Based Routing**:
```
frontend http_in
    bind *:80

    # Define ACLs
    acl is_api path_beg /api
    acl is_static path_beg /static
    acl is_admin hdr(host) -i admin.

    # Use ACLs for routing
    use_backend api_backend if is_api
    use_backend static_backend if is_static
    use_backend admin_backend if is_admin

    # Default
    default_backend web_backend
```

## Backend Configuration

### Basic Backend Pool
```
backend web_backend
    mode http

    # Load balancing algorithm
    balance roundrobin

    # Health check
    option httpchk GET /health HTTP/1.1\r\nHost:\ localhost

    # Server timeout
    timeout server 50000

    # Servers
    server web1 192.168.1.10:80 check inter 5000 rise 2 fall 3
    server web2 192.168.1.11:80 check inter 5000 rise 2 fall 3
    server web3 192.168.1.12:80 check inter 5000 rise 2 fall 3
```

### Backend with Session Persistence
```
backend web_backend
    mode http
    balance roundrobin

    # Cookie-based session persistence
    cookie JSESSIONID insert indirect nocache

    # Health check
    option httpchk GET /health

    # Servers with cookie
    server web1 192.168.1.10:80 check cookie web1
    server web2 192.168.1.11:80 check cookie web2
    server web3 192.168.1.12:80 check cookie web3
```

### TCP Backend (Database)
```
backend mysql_backend
    mode tcp

    # No keep-alive for TCP
    option tcp-check

    # Connection timeout
    timeout server 30000

    # Least connections for stateful
    balance leastconn

    # Servers
    server mysql1 192.168.1.20:3306 check
    server mysql2 192.168.1.21:3306 check backup
```

## Load Balancing Algorithms

### Round Robin
```
backend web_backend
    balance roundrobin  # Default
    server web1 192.168.1.10:80
    server web2 192.168.1.11:80
```

### Least Connections
```
backend web_backend
    balance leastconn
    server web1 192.168.1.10:80
    server web2 192.168.1.11:80
```

### Source IP Hash
```
backend web_backend
    balance source  # Hash on client IP
    server web1 192.168.1.10:80
    server web2 192.168.1.11:80
```

### Weighted Round Robin
```
backend web_backend
    balance roundrobin
    server web1 192.168.1.10:80 weight 3
    server web2 192.168.1.11:80 weight 2
    server web3 192.168.1.12:80 weight 1
```

### URI Hash
```
backend web_backend
    balance uri  # Hash on request URI
    server web1 192.168.1.10:80
    server web2 192.168.1.11:80
```

## Advanced ACL and Routing

### ACL Examples
```
frontend http_in
    bind *:80

    # Path-based ACLs
    acl is_api path_beg /api
    acl is_admin path_beg /admin
    acl is_static path_reg .*\.(jpg|css|js|png|txt|html|gif)$

    # Host-based ACLs
    acl api_host hdr(host) -i api.example.com
    acl www_host hdr(host) -i www.example.com

    # Method-based ACLs
    acl is_post method POST
    acl is_get method GET

    # Source IP ACLs
    acl local_ip src 192.168.0.0/16
    acl trusted_ip src 203.0.113.1 203.0.113.2

    # Header-based ACLs
    acl is_mobile hdr_sub(User-Agent) -i mobile
    acl has_auth hdr_cnt(authorization) gt 0

    # Routing with ACLs
    use_backend api_backend if is_api
    use_backend admin_backend if is_admin is_post
    use_backend static_backend if is_static
    use_backend api_backend if api_host
    use_backend web_backend if www_host

    default_backend web_backend
```

### Request Manipulation with ACLs
```
frontend http_in
    bind *:80

    # Mobile detection and backend routing
    acl is_mobile hdr_sub(User-Agent) -i mobile
    use_backend mobile_backend if is_mobile

    # Rate limiting
    acl too_fast rate gt 100/s
    http-request deny if too_fast

    # Block certain paths
    acl exploit_path path_beg /vulnerable
    http-request deny if exploit_path

    default_backend web_backend
```

## SSL/TLS Configuration

### Certificate Management
```
# Convert certificate to PEM format (if needed)
cat example.com.crt example.com.key > example.com.pem

# Verify certificate
openssl x509 -in example.com.pem -text -noout

# Set permissions
chmod 600 example.com.pem
```

### SSL Configuration
```
frontend https_in
    bind *:443 ssl crt /etc/ssl/certs/example.com.pem

    # TLS versions
    ssl-default-bind-options ssl-min-ver TLSv1.2 ssl-max-ver TLSv1.3

    # Ciphers
    ssl-default-bind-ciphers ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256

    # Session configuration
    tune ssl default-dh-param 2048

    default_backend web_backend
```

### SSL Bridging (Re-encryption)
```
backend web_backend_https
    mode http

    # HTTPS to backend
    server web1 192.168.1.10:443 ssl verify none
    server web2 192.168.1.11:443 ssl verify none

    # verify none: Don't check backend certificate (not production!)
    # For production, use: verify required ca-file /path/to/ca.pem
```

## Health Checking

### HTTP Health Check
```
backend web_backend
    mode http

    # HTTP health check
    option httpchk GET /health HTTP/1.1\r\nHost:\ localhost

    # Expected response status
    http-check expect status 200

    # Servers with health check
    server web1 192.168.1.10:80 check inter 5000 rise 2 fall 3
```

### TCP Health Check
```
backend mysql_backend
    mode tcp

    # TCP connection check
    option tcp-check
    tcp-check connect port 3306

    # Custom command check
    tcp-check send "PING\r\n"
    tcp-check expect string "PONG"

    server mysql1 192.168.1.20:3306 check inter 10000 rise 2 fall 2
```

### Health Check Parameters
```
check:              Enable health check
inter <msec>:       Check interval (5000ms default)
rise <count>:       Passes to mark UP (2 default)
fall <count>:       Failures to mark DOWN (3 default)
weight <value>:     Server weight
maxconn <num>:      Max connections to server
disabled:           Start disabled
backup:             Backup server (only if primary down)
```

## Monitoring and Statistics

### Stats Page
```
frontend stats
    bind *:8404

    stats enable
    stats uri /stats
    stats refresh 30s
    stats admin if TRUE

    # Restrict access (optional)
    acl admin_ip src 203.0.113.1
    stats admin if admin_ip
```

**Access via**: http://your-haproxy:8404/stats

### Enable Logging
```
global
    log 127.0.0.1 local0 info
    log 127.0.0.1 local1 notice
    log-send-hostname

defaults
    log global
    option httplog
    option dontlog-normal

    # Log format
    log-format "%ci:%cp [%tr] %ft %b/%s %TR/%Tw/%Tc/%Tr/%Ta %ST %B %CC %CS %tsc %ac/%fc/%bc/%sc/%rc %sq/%bq %hr %hs %{+Q}r"
```

### View Logs
```bash
tail -f /var/log/haproxy.log
```

## Troubleshooting

### Check Configuration
```bash
haproxy -c -f /etc/haproxy/haproxy.cfg

# Output should show: Configuration file is valid
```

### Reload Configuration (No Downtime)
```bash
sudo systemctl reload haproxy

# Or
sudo haproxy -f /etc/haproxy/haproxy.cfg -p /var/run/haproxy.pid -sf $(cat /var/run/haproxy.pid)
```

### Debug Connections
```bash
# Monitor real-time connections
watch -n 1 'echo "show stat" | socat stdio /var/run/haproxy.sock | grep -E "^.*,,|^(Frontend|Backend)" | head -20'

# Check specific backend
echo "show backend" | socat stdio /var/run/haproxy.sock
```

### Common Issues

**502 Bad Gateway**:
```
Cause: Backend not responding
Solution:
  1. Check backend health: Stats page
  2. Check backend connectivity: ping
  3. Check firewall rules
  4. Check health check endpoint
```

**Connection Refused**:
```
Cause: HAProxy port not listening or firewall blocking
Solution:
  1. Verify bind port: netstat -tulpn | grep haproxy
  2. Check firewall: ufw allow 80/tcp
  3. Verify configuration syntax
  4. Check HAProxy running: ps aux | grep haproxy
```

---

**Last Updated**: 2025-11-19
**Version**: 2.0
