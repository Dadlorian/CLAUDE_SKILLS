# DNS Deployment Guide

## Prerequisites

- Domain registered with registrar
- 2+ dedicated servers (for NS redundancy)
- Basic Linux/Unix knowledge
- Network connectivity for DNS queries

## Step 1: Plan DNS Infrastructure

### Network Diagram
```
Internet
    |
 Root Nameserver (redirects to TLD)
    |
TLD Nameserver (redirects to your authoritative)
    |
┌─────────────────────────────┐
│  Authoritative Nameservers  │
├─────────────────────────────┤
│  ns1.example.com (192.0.2.1)│
│  ns2.example.com (192.0.2.2)│
│  ns3.example.com (192.0.2.3)│
└─────────────────────────────┘
    |           |          |
[Primary]   [Secondary]  [Secondary]
[BIND]      [BIND]       [BIND]
```

### Requirements
- Primary (master) server: Read-write zone management
- Secondary (slave) servers: Read-only copies for redundancy
- Minimum: 2 nameservers (RFC requirement)
- Best practice: 3-4 nameservers
- Geographic distribution: Different cities/regions

## Step 2: Install DNS Server

### Install BIND 9
```bash
# Ubuntu/Debian
apt-get update
apt-get install -y bind9 bind9-utils dnsutils

# RHEL/CentOS
yum install -y bind bind-utils bind-libs

# Verify installation
named -v
# BIND 9.18.x or newer
```

### Directory Structure
```
/etc/bind/
├── named.conf                 # Main config file
├── named.conf.options         # Resolver options
├── named.conf.local           # Zone definitions
├── zones/
│   ├── db.example.com         # Zone file (primary)
│   ├── db.0.0.192.in-addr.arpa # Reverse zone
│   └── db.root                # Root hints
└── keys/
    └── rndc.key              # Control authentication
```

## Step 3: Configure Primary Nameserver

### named.conf.local
```
// Zone definitions for master server
zone "example.com" {
    type master;
    file "/etc/bind/zones/db.example.com";
    allow-transfer { 192.0.2.2; 192.0.2.3; };  // Secondary servers
    notify yes;  // Notify secondaries on update
    also-notify { 192.0.2.2; 192.0.2.3; };
};

// Reverse zone
zone "0.0.192.in-addr.arpa" {
    type master;
    file "/etc/bind/zones/db.192.0.0";
    allow-transfer { 192.0.2.2; 192.0.2.3; };
};
```

### Create Zone File
```bash
sudo nano /etc/bind/zones/db.example.com
```

Zone file content:
```
$TTL 3600
$ORIGIN example.com.

; SOA record (Start of Authority)
@    IN    SOA    ns1.example.com. admin.example.com. (
           2024111901    ; Serial (YYYYMMDDNN format)
           3600          ; Refresh (1 hour)
           1800          ; Retry (30 minutes)
           604800        ; Expire (7 days)
           86400 )       ; Minimum TTL (1 day)

; Nameservers
@    IN    NS    ns1.example.com.
@    IN    NS    ns2.example.com.
@    IN    NS    ns3.example.com.

; Nameserver A records
ns1    IN    A    192.0.2.1
ns2    IN    A    192.0.2.2
ns3    IN    A    192.0.2.3

; Mail exchange
@    IN    MX    10    mail.example.com.
mail IN    A    192.0.2.20

; Web server
@    IN    A    192.0.2.10
www  IN    A    192.0.2.10

; Subdomains
api  IN    A    192.0.2.30
cdn  IN    CNAME    d111111abcdef8.cloudfront.net.
```

### Set Permissions
```bash
sudo chown bind:bind /etc/bind/zones/db.example.com
sudo chmod 644 /etc/bind/zones/db.example.com
```

## Step 4: Configure Secondary Nameservers

### named.conf.local (Secondary)
```
zone "example.com" {
    type slave;
    file "/var/cache/bind/db.example.com";
    masters { 192.0.2.1; };  // Primary server IP
    allow-notify { 192.0.2.1; };
};

zone "0.0.192.in-addr.arpa" {
    type slave;
    file "/var/cache/bind/db.192.0.0";
    masters { 192.0.2.1; };
};
```

### Verify Zone Transfer
```bash
# Test zone transfer from primary
dig @192.0.2.1 example.com AXFR

# Test secondary can answer
dig @192.0.2.2 example.com A
```

## Step 5: Start and Test

### Start BIND
```bash
# Enable service
systemctl enable named

# Start service
systemctl start named

# Check status
systemctl status named

# View logs
tail -f /var/log/syslog | grep named
```

### Test DNS Resolution
```bash
# Test from local machine
nslookup example.com 192.0.2.1

# Test specific record type
dig @192.0.2.1 example.com A
dig @192.0.2.1 example.com MX
dig @192.0.2.1 example.com NS

# Test reverse DNS
dig -x 192.0.2.10 @192.0.2.1

# Test recursive query (should fail at localhost)
dig @127.0.0.1 example.com
```

### Validate Zone File
```bash
# Check syntax
sudo named-checkzone example.com /etc/bind/zones/db.example.com

# Output:
# zone example.com/IN: loaded serial 2024111901
# OK
```

## Step 6: Update Registrar

### Get Nameserver IPs
```bash
# Verify your nameserver addresses
nslookup ns1.example.com
nslookup ns2.example.com
nslookup ns3.example.com

# Example output:
# ns1.example.com has address 192.0.2.1
# ns2.example.com has address 192.0.2.2
# ns3.example.com has address 192.0.2.3
```

### Register Nameservers
1. Log in to registrar (GoDaddy, Namecheap, etc.)
2. Go to Domain Management
3. Change Nameservers
4. Enter:
   - ns1.example.com (192.0.2.1)
   - ns2.example.com (192.0.2.2)
   - ns3.example.com (192.0.2.3)
5. Save changes
6. Wait for propagation (15 minutes to 24 hours)

### Verify Propagation
```bash
# Check using public nameserver
dig @8.8.8.8 example.com NS

# Should show your nameservers:
# example.com.    3600    IN    NS    ns1.example.com.
# example.com.    3600    IN    NS    ns2.example.com.
# example.com.    3600    IN    NS    ns3.example.com.

# Verify resolution works globally
dig @8.8.8.8 www.example.com A
# Should return your IP
```

## Step 7: Test from External Machines

### Query from External Host
```bash
# From another computer on internet
dig @ns1.example.com www.example.com A

# Should return A record
# www.example.com.    3600    IN    A    192.0.2.10
```

### Use Public Tools
```
Online DNS Checkers:
- https://dnschecker.org/
- https://mxtoolbox.com/
- https://whatsmydns.net/

All should show your nameservers and IPs
```

## Step 8: Monitor and Maintain

### Daily Monitoring
```bash
# Check DNS query logs
tail -f /var/log/bind/query.log

# Monitor nameserver health
watch -n 5 'dig @ns1.example.com example.com A'

# Check zone serial (should increment on changes)
dig example.com SOA +short
```

### Maintenance Tasks
```bash
# Update zone (increment serial)
nano /etc/bind/zones/db.example.com
# Change serial: 2024111901 -> 2024111902

# Reload zone (without restart)
rndc reload example.com

# Reload entire BIND
rndc reload

# Flush BIND cache
rndc flush

# Check BIND status
rndc status
```

### Monitoring Script
```bash
#!/bin/bash
# dns-health-check.sh

# Check all nameservers respond
for ns in ns1 ns2 ns3; do
    response=$(dig @${ns}.example.com example.com A +short)
    if [ $? -eq 0 ]; then
        echo "✓ $ns: OK"
    else
        echo "✗ $ns: FAILED"
        # Alert: email ops, page on-call, etc.
    fi
done
```

## Troubleshooting

### Issue: Zone Transfer Fails
```
Error: refused

Solution:
1. Check firewall allows port 53 TCP
2. Verify allow-transfer in named.conf
3. Check secondary IP is whitelisted
4. Verify slave zone masters IP is correct

Command to test:
sudo ufw allow from 192.0.2.2 to any port 53/tcp
```

### Issue: Queries Return REFUSED
```
dig @ns1.example.com example.com
; <<>> DiG 9.18.x <<>> @ns1.example.com example.com
; (1 server found)
;; ->>HEADER<<- opcode: QUERY, status: REFUSED
```

Solution:
- Check zone definition exists in named.conf.local
- Verify zone file path is correct
- Check zone file permissions (bind:bind)
- Reload BIND: `rndc reload`

### Issue: Serial Number Not Incrementing
```
rndc notify example.com
# Forces NOTIFY to secondaries regardless of serial

# For testing, temporarily lower SOA refresh
; Refresh = 10s (for testing)
```

### Issue: Slow Queries
```bash
# Enable query logging
rndc querylog on

# Check slow queries
tail -f /var/log/bind/query.log | grep example.com

# Increase cache:
max-cache-size 256M;  # in named.conf options
```

## Security Hardening

### Restrict Zone Transfers
```
// Only allow secondaries, not public
allow-transfer { 192.0.2.2; 192.0.2.3; };

// Deny all by default
allow-transfer { none; };
```

### Disable Recursion
```
// For authoritative-only server
recursion no;
allow-recursion { none; };
```

### Rate Limiting
```
rate-limit {
    responses-per-second 20;
    nxdomain-per-second 10;
    all-per-second 100;
    errors-per-second 5;
};
```

### Enable DNSSEC
See: dnssec_implementation_guide.md

## Production Checklist

- [ ] At least 2 nameservers deployed
- [ ] Nameservers in different locations
- [ ] Zone file syntax validated
- [ ] Zone transfers working
- [ ] Registrar updated with nameserver IPs
- [ ] DNS propagation verified (8.8.8.8 query)
- [ ] External queries work
- [ ] Health monitoring in place
- [ ] Backup zone files stored
- [ ] Emergency contacts documented
- [ ] DNSSEC considered/deployed
- [ ] Monitoring alerts configured
- [ ] Disaster recovery tested
