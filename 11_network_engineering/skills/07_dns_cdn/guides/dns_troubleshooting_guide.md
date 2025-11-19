# DNS Troubleshooting Guide

## Diagnostic Tools

### Essential Commands

**dig - DNS Lookup Tool**
```bash
# Basic query
dig example.com

# Specify nameserver
dig @ns1.example.com example.com

# Query specific record type
dig example.com MX
dig example.com TXT
dig example.com NS

# Show full details
dig example.com +noall +answer
dig example.com +trace  # Show full query path to root

# Short output
dig example.com +short

# Reverse DNS
dig -x 192.0.2.1
```

**nslookup - DNS Lookup**
```bash
# Basic query
nslookup example.com

# Specify nameserver
nslookup example.com ns1.example.com

# Reverse DNS
nslookup 192.0.2.1
```

**host - Simple DNS Lookup**
```bash
# Query
host example.com

# Get all records
host -a example.com

# Reverse DNS
host 192.0.2.1
```

**whois - Domain Information**
```bash
# Get domain info
whois example.com

# Get AS information
whois -h whois.arin.net 203.0.113.0
```

## Common DNS Issues

### Issue 1: Domain Not Resolving

**Symptoms:**
```
$ dig example.com
; <<>> DiG 9.18.x <<>> example.com
;; ANSWER SECTION: (empty)
;; AUTHORITY SECTION: (empty)
```

**Diagnosis:**

Step 1: Check if domain is registered
```bash
whois example.com
# Should show domain registration info
```

Step 2: Check nameservers
```bash
dig example.com NS

# Should show NS records
# example.com.    3600    IN    NS    ns1.example.com.
# example.com.    3600    IN    NS    ns2.example.com.
```

Step 3: Query specific nameserver
```bash
dig @ns1.example.com example.com

# If this works, issue is with resolver
# If this fails, issue is with nameserver
```

Step 4: Check propagation
```bash
# Use online tools
nslookup example.com 8.8.8.8  # Google DNS
nslookup example.com 1.1.1.1  # Cloudflare DNS

# Different results = propagation issue (wait 24-48 hours)
```

**Solutions:**
- Registrar: Verify nameservers set correctly
- DNS Server: Ensure zone file exists and is loaded
- Firewall: Check port 53 UDP/TCP open
- Propagation: Wait for TTL expiration (24-48 hours typical)

### Issue 2: Slow DNS Resolution

**Symptoms:**
```bash
$ time dig example.com
; Query time: 500 msec (should be < 100 msec)
```

**Diagnosis:**

Step 1: Check query time per nameserver
```bash
dig @ns1.example.com example.com  # 50ms (fast)
dig @ns2.example.com example.com  # 2000ms (slow)

# Identify slow nameserver
```

Step 2: Check network connectivity
```bash
# Ping nameserver
ping -c 3 ns1.example.com
# Latency: 50ms (normal) vs 500ms+ (slow network)

# Traceroute to nameserver
traceroute ns1.example.com
# Identify slow hop
```

Step 3: Check resolver cache
```bash
# Clear system cache
# macOS:
dscacheutil -flushcache

# Linux:
systemd-resolve --flush-caches

# Windows:
ipconfig /flushdns

# Then test again
```

**Solutions:**
- Network: Check connectivity to slow nameserver (packet loss, latency)
- Cache: Flush resolver cache
- Load: Check nameserver CPU/load (may be overloaded)
- Configuration: May need more nameservers or caching layer

### Issue 3: Intermittent Resolution Failures

**Symptoms:**
```bash
$ for i in {1..5}; do dig example.com +short; done
192.0.2.1
192.0.2.2
(empty - FAILED)
192.0.2.1
192.0.2.2
```

**Diagnosis:**

Step 1: Check all nameservers
```bash
# Query each NS individually
for ns in ns1 ns2 ns3; do
  echo "Testing $ns:"
  dig @${ns}.example.com example.com +short
done

# One is likely failing
```

Step 2: Check nameserver health
```bash
# Ping each nameserver
ping ns1.example.com
ping ns2.example.com
ping ns3.example.com

# One may be unreachable
```

Step 3: Check firewall rules
```bash
# Verify port 53 open
telnet ns1.example.com 53

# Check iptables (Linux)
sudo iptables -L -n | grep 53
```

**Solutions:**
- Failing NS: Fix or remove from NS records
- Firewall: Allow port 53 UDP/TCP
- Network: Check connectivity to failing nameserver
- DNS Config: Verify zone transferred to all secondaries

### Issue 4: Wrong Answer (NXDOMAIN)

**Symptoms:**
```bash
$ dig mail.example.com
; <<>> DiG 9.18.x <<>> mail.example.com
;; status: NXDOMAIN
```

**Diagnosis:**

Step 1: Verify record exists
```bash
# Check zone file for record
cat /etc/bind/zones/db.example.com | grep mail

# Should show:
# mail    IN    A    192.0.2.20

# If not present, record missing
```

Step 2: Check nameserver has zone
```bash
dig @ns1.example.com example.com SOA

# Should return SOA record
# If NXDOMAIN, nameserver doesn't have zone
```

Step 3: Verify zone transfer
```bash
# Manually check secondary
dig @ns2.example.com mail.example.com

# If works on primary but not secondary
# = zone transfer issue
```

**Solutions:**
- Missing Record: Add to zone file and reload
- Zone Transfer: Check allow-transfer, TSIG keys
- DNS Config: Verify zone file path in named.conf
- Reload: Run `rndc reload` after changes

### Issue 5: DNSSEC Validation Failures

**Symptoms:**
```bash
$ dig @8.8.8.8 example.com +dnssec
;; ->>HEADER<<- opcode: QUERY, status: SERVFAIL
; (DNSSEC validation failed)
```

**Diagnosis:**

Step 1: Check DNSSEC is signed
```bash
dig example.com DNSKEY
dig example.com RRSIG A

# Both should return records
# If missing, zone not signed
```

Step 2: Validate DS record in parent
```bash
# Check DS record exists
dig example.com DS @parent.nameserver

# Should show DS record from parent
# If missing, not linked to parent
```

Step 3: Check signature expiration
```bash
dig example.com RRSIG A +short

# Find expiration field (7th field)
# Compare to current time
# If expired, re-sign zone
```

**Solutions:**
- Not Signed: Run `dnssec-signzone`
- Missing DS: Submit to registrar
- Expired Signature: Re-sign zone or enable auto-signing
- Chain Broken: Verify DNSKEY in child, DS in parent match

## Troubleshooting Workflows

### Workflow 1: New Domain Not Resolving

```
1. whois domain.com
   → Verify domain registered and active

2. dig domain.com NS
   → Verify NS records appear

3. dig @ns1.domain.com domain.com A
   → Query authoritative server directly

   a) If returns IP:
      - Issue is resolver not updated
      - Check registrar NS settings
      - Wait for propagation
      - Clear local cache

   b) If NXDOMAIN:
      - Issue is with nameserver
      - Check zone file exists
      - Check named.conf includes zone
      - Check zone file syntax (named-checkzone)
      - Reload BIND

4. dig @8.8.8.8 domain.com
   → Test from public resolver
   → Should work after propagation
```

### Workflow 2: DNS Returning Wrong IP

```
1. dig example.com A +short
   → Note the returned IP

2. Verify expected IP
   # What should it be?
   # Check records:
   cat /etc/bind/zones/db.example.com | grep "^@"

   a) If zone file correct:
      - TTL not expired on clients
      - Clear local cache
      - Wait for TTL
      - Can force with lower TTL

   b) If zone file wrong:
      - Update zone file
      - Increment SOA serial
      - Reload BIND

3. Check all nameservers consistent
   for ns in ns1 ns2 ns3; do
     dig @${ns}.example.com example.com A +short
   done
   # All should return same IP
```

### Workflow 3: Recursive Query Failures

```
1. dig @localhost example.com
   → Test recursive resolver locally

2. Check resolver allowed recursion
   # In /etc/bind/named.conf
   allow-recursion { internal-networks; };

   a) If client IP not in ACL:
      - Add client IP to recursion ACL
      - Reload BIND

   b) If recursion disabled:
      - Enable: recursion yes;
      - Reload BIND

3. Check forwarders configured
   # If forwarding to upstream:
   forwarders { 8.8.8.8; };

   a) Test upstream resolver:
      dig @8.8.8.8 example.com

   b) If upstream failing:
      - Change forwarder
      - Or enable recursion to root
```

## Performance Troubleshooting

### Slow Query Times

```bash
# Benchmark query time
for i in {1..10}; do
  dig @ns1.example.com example.com | grep "Query time"
done

# Average times:
# < 50ms: Excellent
# 50-100ms: Good
# 100-500ms: Acceptable
# > 500ms: Poor (investigate)
```

**Performance Issues:**

1. **Slow Network**
```bash
# Check RTT to nameserver
ping -c 10 ns1.example.com

# If latency > 200ms, network issue
# Use closer nameserver or check network path
```

2. **Overloaded Nameserver**
```bash
# Check CPU on nameserver
ssh ns1.example.com uptime

# If load > num_cores, overloaded
# Reduce query load or scale horizontally
```

3. **Large Response**
```bash
# Check response size
dig example.com AXFR | wc -l

# Large zone = slow transfer
# Consider splitting zones
```

## Log Analysis

### Enable Query Logging

BIND:
```
logging {
  channel query_log {
    file "/var/log/bind/query.log";
    print-time yes;
  };
  category queries { query_log; };
};
```

### Analyze Logs

```bash
# Find slowest queries
tail -1000 /var/log/bind/query.log | \
  awk '{print $(NF-1)}' | sort -rn | head -20

# Find most common queries
grep "query:" /var/log/bind/query.log | \
  awk '{print $7}' | sort | uniq -c | sort -rn | head -20

# Find failed queries
grep "REFUSED\|SERVFAIL\|NXDOMAIN" /var/log/bind/query.log

# Find queries by IP
grep "192.0.2.1" /var/log/bind/query.log
```

## Tools and Utilities

### Online Tools
- **MXToolbox**: https://mxtoolbox.com/
- **DNS Checker**: https://dnschecker.org/
- **WhatIsMyDNS**: https://whatsmydns.net/
- **DNSSEC Analyzer**: https://dnssec-analyzer.verisignlabs.com/

### Commands Reference
```bash
dig                 # Full DNS information
nslookup           # Simple lookup
host               # Quick lookup
whois              # Domain information
traceroute         # Network path
mtr                # Continuous traceroute
tcpdump            # Packet capture
wireshark          # GUI packet analyzer
rndc               # BIND control
named-checkzone    # Zone file validation
dnssec-validate    # DNSSEC validation
```

## Quick Fixes

| Issue | Quick Fix |
|-------|-----------|
| Domain doesn't resolve | Wait 24-48h for NS propagation |
| Wrong IP returned | Update zone file, increment serial, reload |
| Slow resolution | Clear cache, check network latency |
| DNSSEC failing | Submit DS to registrar, wait for propagation |
| Recursive queries fail | Add client IP to allow-recursion ACL |
| Zone transfer failing | Verify allow-transfer, check TSIG keys |
| Nameserver down | Add redundant nameserver, update NS records |
| High DNS load | Implement caching layer, scale nameservers |

## Prevention

**Regular Checks:**
```bash
# Daily: Query all nameservers
for ns in ns1 ns2 ns3; do
  dig @${ns}.example.com example.com A +short
done

# Weekly: Verify DNSSEC
dig example.com DNSKEY RRSIG

# Monthly: Full audit
dig example.com NS +short
dig example.com SOA +short
dig example.com A MX TXT +short
```

**Monitoring:**
- Set up CloudWatch/Grafana dashboards
- Alert on query failures (> 1% failure rate)
- Alert on slow queries (p95 > 500ms)
- Alert on DNSSEC signature expiration (< 7 days)
