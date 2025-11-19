# Load Balancer Troubleshooting Guide

## Systematic Troubleshooting Approach

### OSI Layer Model Troubleshooting
```
Layer 1 (Physical):
  - Network cables connected
  - Interfaces operational
  - No hardware errors

Layer 2 (Data Link):
  - MAC addresses resolved
  - VLAN configuration correct
  - Spanning tree stable

Layer 3 (Network):
  - IP addresses configured
  - Routes valid
  - Firewalls allow traffic

Layer 4 (Transport):
  - Ports listening
  - Connections established
  - No timeouts

Layer 5-7 (Application):
  - Service responding
  - Correct data returned
  - Performance acceptable
```

### Troubleshooting Steps
```
1. Gather Information
   - Issue symptoms
   - When it started
   - What changed recently
   - Configuration current

2. Test Baseline
   - Is LB reachable? (ping, SSH)
   - Is service running? (ps, systemctl)
   - Are backends healthy? (curl, logs)

3. Isolate Problem
   - LB configuration issue?
   - Network issue?
   - Backend issue?
   - Client issue?

4. Test Hypothesis
   - Make one change
   - Test result
   - Document finding

5. Implement Fix
   - Apply solution
   - Verify working
   - Monitor stability
```

## Common Load Balancer Issues

### Issue 1: Load Balancer Not Responding

**Symptoms**:
```
- Clients can't connect
- Connection timeout
- "Connection refused" errors
```

**Diagnosis**:
```
Step 1: Is the load balancer running?
  ps aux | grep haproxy
  systemctl status nginx
  show ltm virtual (F5)

Step 2: Is the service listening on the port?
  netstat -tulpn | grep 80
  netstat -tulpn | grep 443

Step 3: Is the interface up?
  ip link show
  ifconfig
  show net interface (F5)

Step 4: Firewall blocking?
  sudo ufw status
  sudo iptables -L
  Cloud security group rules
```

**Resolution**:
```
If service not running:
  systemctl start haproxy
  systemctl start nginx

If port not listening:
  Check configuration for errors
  haproxy -c -f /etc/haproxy/haproxy.cfg
  nginx -t

If firewall blocking:
  Allow port 80/443 inbound
  ufw allow 80/tcp
  ufw allow 443/tcp
```

### Issue 2: Backend Servers Marked DOWN

**Symptoms**:
```
- Health check failures
- Servers shown as DOWN in stats
- Traffic not reaching backends
- Error messages in logs
```

**Diagnosis**:
```
Step 1: Check health check results
  HAProxy Stats page:
    show stat | grep backend_name
  F5:
    show ltm pool pool_name members
  NGINX Plus:
    Dashboard > Upstream > Server status

Step 2: Manual health check
  curl http://192.168.1.10:80/health
  curl https://192.168.1.10:443/health
  Telnet 192.168.1.10 3306

Step 3: Check network connectivity
  ping 192.168.1.10
  traceroute 192.168.1.10
  arp -n | grep 192.168.1.10

Step 4: Check firewall rules
  From LB: ping backend
  From LB: nc -zv backend_ip backend_port
  Verify security groups allow traffic

Step 5: Check backend service
  ssh backend_server
  systemctl status httpd
  ps aux | grep nginx
  netstat -tulpn | grep :80
```

**Resolution**:
```
Backend service not running:
  systemctl start httpd
  systemctl start nginx
  systemctl start mysql

Network connectivity issue:
  Check network cable
  Check IP configuration
  Check routing
  Open firewall rule

Health check endpoint broken:
  curl http://backend/health (should work)
  Check backend logs for errors
  Fix health endpoint

Health check too strict:
  Adjust thresholds: rise/fall counts
  Increase timeout
  Change health check path
  Add dependency checks
```

### Issue 3: Unbalanced Load Distribution

**Symptoms**:
```
- Some servers get more traffic
- Some servers underutilized
- Resource distribution uneven
```

**Diagnosis**:
```
Step 1: Check load balancing algorithm
  HAProxy: balance roundrobin/leastconn/source
  NGINX: least_conn/ip_hash/random
  F5: Round Robin/Least Connections/Response Time

Step 2: Check server health
  Is each server HEALTHY?
  Any servers DOWN or DISABLED?
  All in AVAILABLE state?

Step 3: Check connection distribution
  HAProxy stats: Req rate, Req total per server
  NGINX stats: Connections per upstream server
  Monitor real-time requests

Step 4: Check for affinity
  Clients should distribute across backends
  If using IP hash, clients from same subnet?
```

**Resolution**:
```
If using IP hash with skewed distribution:
  - Check if many clients from same IP (NAT/proxy)
  - Switch to least connections
  - Use weighted algorithm

If some servers down:
  - Mark DOWN servers as disabled
  - Remove from pool
  - Fix and re-enable

If servers have different capacity:
  - Use weighted load balancing
  - Assign appropriate weights
  - Example: 4CPU = weight 2, 2CPU = weight 1
```

### Issue 4: Session Not Persisting

**Symptoms**:
```
- Session lost between requests
- User logged out unexpectedly
- Shopping cart emptied
- Form data lost
```

**Diagnosis**:
```
Step 1: Check session configuration
  Is persistence configured?
  Cookie-based or IP hash?
  Timeout settings correct?

Step 2: Check if cookie present
  curl -v http://example.com
  Look for Set-Cookie header
  Check cookie value

Step 3: Verify routing
  Manual test with same cookie
  curl -H "Cookie: JSESSIONID=abc123" ...
  Does it go to same backend?

Step 4: Check backend sessions
  SSH to backend 1, 2, 3
  Check session storage
  Is session file present?
  Check permissions

Step 5: Check session replication
  If using Redis, is it running?
  redis-cli ping
  Check connection from backend
```

**Resolution**:
```
If persistence not configured:
  Add cookie-based persistence
  Configure sticky sessions

If cookie not being set:
  Check application
  Verify health endpoint returns cookies
  Enable cookie in proxy settings

If routing not sticky:
  Verify LB config:
    HAProxy: cookie JSESSIONID insert
    NGINX: sticky cookie
    F5: persistence cookie

If session lost on backend failure:
  Implement session replication:
    - Use Redis, Memcached
    - Or database session store
    - Sync sessions across backends
```

### Issue 5: SSL/TLS Errors

**Symptoms**:
```
- Browser warning about certificate
- "SSL_ERROR_RX_RECORD_TOO_LONG"
- "TLS handshake failed"
- Certificate mismatch errors
```

**Diagnosis**:
```
Step 1: Check certificate
  openssl x509 -in cert.pem -text -noout
  Check expiry date
  Check CN/SAN match domain

Step 2: Test TLS connection
  openssl s_client -connect example.com:443
  Verify certificate chain
  Check TLS version negotiated

Step 3: Check certificate installation
  Is cert installed on LB?
  Is key installed?
  Do permissions allow reading?

Step 4: Check TLS configuration
  Minimum TLS version set?
  Disabled weak ciphers?
  Strong ciphers first?

Step 5: SNI (if multiple certs)
  openssl s_client -servername example.com -connect example.com:443
  Does correct cert returned?
```

**Resolution**:
```
Certificate not valid:
  - Renew certificate before expiry
  - Fix CN/SAN mismatch
  - Install intermediate certificates

Certificate not installed:
  - Upload certificate to LB
  - Configure virtual server with cert
  - Verify in LB config

TLS version negotiation:
  - Ensure client supports TLS 1.2+
  - Check minimum version setting
  - Temporarily lower if testing old clients

SNI not working:
  - Enable SNI in LB config
  - Check hostname matches cert
  - Test with specific hostname
```

### Issue 6: High Response Times

**Symptoms**:
```
- Slow response times
- Users reporting lag
- Applications timing out
- P95/P99 latency high
```

**Diagnosis**:
```
Step 1: Baseline Response Time
  curl -w "@curl-format.txt" -o /dev/null -s https://example.com
  Time_Connect, Time_AppConnect, Time_Redirect, Time_FirstByte

Step 2: Where is latency?
  TLS handshake slow?
  Network path slow?
  Backend slow?
  LB processing slow?

Step 3: Check LB CPU/Memory
  HAProxy: top, htop
  NGINX: top, nginx -T
  F5: show sys performance

Step 4: Check backend latency
  curl http://backend_direct
  Compare to through LB
  Difference = LB overhead

Step 5: Check network
  traceroute to backend
  ping response times
  Network congestion?
```

**Resolution**:
```
TLS handshake slow:
  - Enable session resumption
  - Use hardware acceleration
  - Adjust cipher order

LB CPU high:
  - Add more LB capacity
  - Enable connection pooling
  - Reduce SSL/TLS processing

Backend slow:
  - Fix application
  - Increase backend resources
  - Scale backends horizontally

Network slow:
  - Check network path
  - Verify no congestion
  - Monitor link utilization
```

### Issue 7: Connection Errors from Clients

**Symptoms**:
```
- "Connection refused"
- "Connection timeout"
- Intermittent failures
- Random backend unavailable errors
```

**Diagnosis**:
```
Step 1: Check error rate
  Is it consistent?
  Does it correspond to specific requests?
  Is pattern observable?

Step 2: Check backend availability
  Are all backends healthy?
  Connection count high?
  Max connections reached?

Step 3: Check health check
  When last failed?
  Is timing consistent?
  Does correspond to error times?

Step 4: Check network
  Packet loss?
  Latency spikes?
  Connection resets?

Step 5: Application logs
  Backend error logs
  LB access logs
  Network tcpdump
```

**Resolution**:
```
Backend capacity exceeded:
  - Increase max connections
  - Add more backends
  - Implement queuing

Health check issues:
  - Fix health endpoint
  - Adjust thresholds
  - Increase timeout

Network problems:
  - Check network path
  - Verify no packet loss
  - Monitor latency

Connection limit reached:
  - Increase ulimits
  - Adjust LB connection limits
  - Enable connection pooling
```

## Tools and Commands

### Useful Commands

**HAProxy**:
```bash
# Show stats
echo "show stat" | socat stdio /var/run/haproxy.sock

# Show current sessions
echo "show sess" | socat stdio /var/run/haproxy.sock

# Disable backend
echo "disable server backend/web1" | socat stdio /var/run/haproxy.sock

# Enable backend
echo "enable server backend/web1" | socat stdio /var/run/haproxy.sock

# View configuration
echo "show config" | socat stdio /var/run/haproxy.sock
```

**NGINX**:
```bash
# Test configuration
nginx -t

# View all configuration
nginx -T

# View version info
nginx -v

# Reload configuration
sudo systemctl reload nginx

# View error log
tail -f /var/log/nginx/error.log

# Check upstream servers
curl http://localhost:8080/api/7/http/upstreams/
```

**F5 BIG-IP**:
```bash
# Show virtual server status
show ltm virtual

# Show pool member status
show ltm pool pool_name members

# Show statistics
show sys statistics

# Enable/disable pool member
modify ltm pool pool_name members {
  192.168.1.10:80 {
    state user-down
  }
}

# View iRule
list ltm rule rule_name

# Save configuration
save sys config
```

**General Network Tools**:
```bash
# Test connectivity
ping backend_ip

# Test port connectivity
nc -zv backend_ip 80
telnet backend_ip 80

# HTTP request test
curl -v http://backend_ip/

# DNS resolution
dig example.com
nslookup example.com

# Network traffic capture
tcpdump -i eth0 -n port 80
tcpdump -i eth0 -n host 192.168.1.10

# Connection statistics
netstat -tulpn
netstat -s  # Show statistics

# Trace route
traceroute backend_ip

# Monitor live connections
watch -n 1 'netstat -tulpn | grep ESTABLISHED'
```

## Creating Effective Monitoring

### Alerting Rules
```
Critical Alerts (immediate action):
  - All backends DOWN
  - Error rate > 5%
  - Response time P99 > 5 seconds
  - Certificate expires < 7 days
  - LB CPU > 90%
  - LB memory > 90%

Warning Alerts (prompt investigation):
  - Single backend DOWN
  - Error rate > 1%
  - Response time P95 > 1 second
  - Certificate expires < 30 days
  - LB CPU > 80%
  - LB memory > 80%

Info Alerts (trending):
  - Requests/second increasing
  - Connection count increasing
  - New backend added
  - Configuration changed
```

### Key Metrics to Track
```
Availability:
  - % uptime per backend
  - % uptime per LB
  - Mean time between failures

Performance:
  - Average response time
  - P95 response time
  - P99 response time
  - Requests per second

Errors:
  - 4xx error rate
  - 5xx error rate
  - Connection errors
  - Timeout rate

Capacity:
  - Active connections count
  - New connections per second
  - Bandwidth usage
  - CPU/Memory utilization
```

---

**Last Updated**: 2025-11-19
**Version**: 2.0
