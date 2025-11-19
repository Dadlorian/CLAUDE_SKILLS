# DNS Security Guide

## DNS Security Threats

### Common Attacks

1. **DNS Spoofing/Poisoning**
   - Attacker sends false DNS responses
   - Client caches wrong IP address
   - Traffic redirected to attacker's server

2. **DNS Amplification DDoS**
   - Attacker spoofs victim's IP
   - Queries small domain, gets large response
   - Amplified traffic floods victim

3. **DNS Hijacking**
   - Attacker compromises domain account
   - Changes NS records to attacker's servers
   - All DNS queries go to attacker

4. **Cache Poisoning**
   - Attacker injects records into resolver cache
   - Legitimate queries return poisoned data
   - Affects all users of that resolver

5. **DNS Redirection**
   - Modify DNS to redirect to phishing sites
   - Intercept HTTPS traffic (if certificate spoofed)
   - Steal credentials

## DNSSEC Protection

See: dnssec_implementation_guide.md

DNSSEC cryptographically signs DNS responses, preventing:
- DNS spoofing
- Cache poisoning
- Unauthorized zone modifications

## Rate Limiting

### DNS Query Rate Limiting

**Prevent DNS Amplification Attacks:**

BIND Configuration:
```
rate-limit {
  responses-per-second 20;      # Max 20 responses/sec per client
  nxdomain-per-second 10;       # Max 10 NXDOMAIN/sec per client
  all-per-second 100;           # Max 100 total responses/sec per client
  errors-per-second 5;          # Max 5 error responses/sec per client
  window 15;                    # 15 second window
  log-only no;                  # Actually drop (not just log)
};
```

**Effects:**
- Legitimate clients: Unaffected (normal query rates < limits)
- Attackers: Requests dropped after limit reached
- DDoS mitigation: Reduces amplification potential

### Recursive Query Rate Limiting

**Prevent resource exhaustion:**

```
allow-recursion { 192.0.2.0/24; };  # Only specific networks

# Rate limit recursive queries
recursive-clients 1000;  # Max 1000 concurrent recursive queries

# Limit queries from single IP
rrl-rate 10;  # Max 10 responses/sec per client
```

## Query Authentication

### TSIG (Transaction Signatures)

**Authenticate zone transfers and dynamic updates:**

```bash
# Generate TSIG key
tsig-keygen -a HMAC-SHA256 transfer-key > /etc/bind/keys/transfer.key

# Key format:
key "transfer-key" {
  algorithm HMAC-SHA256;
  secret "xyz789abc012def345ghi678jkl901mno012";
};
```

**Configure BIND for authenticated transfers:**

Primary Server:
```
zone "example.com" {
  type master;
  file "/etc/bind/zones/db.example.com";

  // TSIG authentication
  update-policy {
    grant transfer-key zonesub ANY;  # Allow updates with key
  };
};
```

Secondary Server:
```
zone "example.com" {
  type slave;
  masters { 192.0.2.1 key transfer-key; };  // Require key for transfer
};
```

### DNS UPDATE Authentication

**Allow DDNS only with valid key:**

```
zone "example.com" {
  // Only TSIG-authenticated updates allowed
  update-policy {
    grant transfer-key zonesub ANY;
  };
};

// Deny all other updates
update-policy { deny "*"; };
```

## IP Whitelisting

### Restrict Zone Transfers

**Only allow secondary nameservers:**

```
zone "example.com" {
  allow-transfer {
    192.0.2.2;      # Secondary nameserver 1
    192.0.2.3;      # Secondary nameserver 2
    203.0.113.1;    # Off-site backup server
  };
};

// Default deny all transfers
allow-transfer { none; };
```

### Restrict Query Sources

**Public authoritative DNS:**
```
// Allow queries from anyone (authoritative DNS)
allow-query { any; };
```

**Internal recursive DNS:**
```
// Only allow queries from internal network
allow-query {
  192.0.2.0/24;
  10.0.0.0/8;
};
```

## Access Control Lists (ACLs)

### Define and Use ACLs

```
// Define trusted networks
acl internal-networks {
  192.0.2.0/24;      # Data center 1
  10.0.0.0/8;        # Corporate network
  203.0.113.0/24;    # Backup site
};

acl secondary-servers {
  192.0.2.2;         # ns2.example.com
  192.0.2.3;         # ns3.example.com
};

// Apply ACLs
zone "example.com" {
  allow-query { any; };              # Public queries
  allow-transfer { secondary-servers; };  # Only secondaries
  update-policy {
    grant transfer-key zonesub ANY;   # Only TSIG authenticated
  };
};
```

## DDoS Protection

### DNS Query Validation

**Prevent DNS-based attacks:**

BIND:
```
// Validate DNS query format
dnssec-validation yes;

// Drop invalid queries
lame-ttl 600;  # Cache negative responses

// Response rate limiting (built-in)
rate-limit {
  responses-per-second 20;
  nxdomain-per-second 10;
};
```

### Recursive Query Restrictions

**Prevent reflection attacks:**

```
// Don't answer recursive queries from strangers
allow-recursion { internal-networks; };

// Actually drop non-recursive queries from internet
// (Not answering any query from external)
allow-query {
  any;  // But limited responses (authoritative only)
};
```

### Amplification Prevention

```
// Respond only to valid queries
check-names master ignore;
check-names slave ignore;

// Minimal response for queries
minimal-responses yes;

// Use EDNS(0) with reasonable limits
max-udp-size 512;  # Standard UDP size (prevents amplification)

// Drop DNSSEC validation requests (expensive)
max-recursion-depth 10;
```

## Query Logging & Monitoring

### Enable Query Logging

**BIND Configuration:**

```
// Log channel for DNS queries
logging {
  channel query_log {
    file "/var/log/bind/query.log" versions 10 size 100M;
    print-time yes;
    print-category yes;
    print-severity yes;
  };

  category queries { query_log; };
};
```

**Query Log Format:**
```
19-Nov-2024 10:30:45.123 [ID 12345] query: example.com IN A +E
19-Nov-2024 10:30:45.124 [ID 12346] query: example.com IN MX +E

Fields:
- Timestamp
- Query ID
- Domain
- Record type
- Flags (+E = EDNS, +D = DNSSEC, etc.)
```

### Analyze Query Logs

**Find suspicious patterns:**

```bash
# Count queries per domain
grep "query:" /var/log/bind/query.log | \
  awk '{print $7}' | sort | uniq -c | sort -rn | head -20

# Find failed queries
grep "REFUSED\|SERVFAIL" /var/log/bind/query.log

# Count queries per IP
grep "query:" /var/log/bind/query.log | \
  awk '{print $1, $9}' | sort | uniq -c | sort -rn

# Detect DNS tunneling (unusual query patterns)
grep "TXT" /var/log/bind/query.log  # Excessive TXT queries
grep "CNAME.*CNAME" /var/log/bind/query.log  # CNAME chains
```

### Monitoring Alerts

**CloudWatch Alarms:**

```hcl
resource "aws_cloudwatch_metric_alarm" "dns_refused" {
  alarm_name          = "dns-refused-queries-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "DNSQueries"
  namespace           = "AWS/Route53"
  period              = 300
  statistic           = "Sum"
  threshold           = 1000  # Alert if > 1000 refused queries
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    HostedZoneId = aws_route53_zone.main.zone_id
  }
}
```

## DNSSEC Validation

See: dnssec_reference.md

**Ensure recursive resolvers validate DNSSEC:**

Unbound Configuration:
```
server:
  # Enable DNSSEC validation
  module-config: "validator iterator"
  trust-anchor-file: "/etc/unbound/root.key"

  # Auto-update root keys
  auto-trust-anchor-file-list: "/etc/unbound/root.key"
```

## DNS Firewall

### Block Malicious Domains

**Cloudflare Firewall:**
```
Dashboard:
1. Security → Firewall Rules
2. Create rule: domain matches "*.malware.com"
3. Action: Block
```

**BIND Response Policy Zone (RPZ):**

```
zone "rpz.example.com" {
  type master;
  file "/etc/bind/zones/rpz.example.com";
};

// Apply RPZ to queries
zone "." {
  response-policy { zone "rpz.example.com"; };
};

// RPZ zone file:
$ORIGIN rpz.example.com.
$TTL 60
@  IN SOA ns1.example.com. admin.example.com. (...)

; Block malware domains
malware.com.rpz  IN  CNAME  .  ; Return NXDOMAIN
ads.doubleclick.net.rpz  IN  CNAME  .

; Return specific IP for tracking domains
tracker.com.rpz  IN  A  127.0.0.1

; Log without blocking
suspicious.com.rpz IN  CNAME  logged-domain.rpz.
logged-domain.rpz IN  A  127.0.0.1
```

## TLS Protection

### DNS over TLS (DoT)

**Encrypted DNS queries to resolver:**

BIND Accepting DoT:
```
tls-config default {
  cert-file "/etc/bind/tls/cert.pem";
  key-file "/etc/bind/tls/key.pem";
};

options {
  listen-on tls { 127.0.0.1; };
  tls default;
};
```

Client Configuration:
```bash
# Query over TLS
kdig @resolver.example.com +tls example.com A
```

### DNS over HTTPS (DoH)

**DNS queries via HTTPS:**

Cloudflare Configuration:
```
Dashboard:
1. DNS → DNS settings
2. Enable "DNS over HTTPS"
3. Endpoint: https://example.com/dns-query
```

Client Usage:
```javascript
// JavaScript fetch API
fetch("https://example.com/dns-query?name=example.com&type=A", {
  method: "GET",
  headers: { "accept": "application/dns-json" }
})
.then(response => response.json())
.then(data => console.log(data.Answer));
```

## Security Hardening Checklist

- [ ] DNSSEC implemented and validated
- [ ] Rate limiting configured
- [ ] Zone transfers authenticated (TSIG)
- [ ] Query source IP whitelisting (if applicable)
- [ ] Query logging enabled and monitored
- [ ] Suspicious query patterns alerted on
- [ ] RPZ or firewall for malware domains
- [ ] DoT/DoH enabled for resolver queries
- [ ] Regular security audits scheduled
- [ ] Disaster recovery plan in place
- [ ] Key backup/rotation procedure documented
- [ ] Team trained on DNS security
- [ ] Incident response plan documented

## Regular Security Maintenance

**Weekly:**
- Review query logs for anomalies
- Check DNS query response times
- Verify all nameservers responding

**Monthly:**
- Audit DNS records for unauthorized changes
- Review DNSSEC signatures (not expired)
- Test failover and recovery

**Quarterly:**
- DNSSEC key rotation exercise
- Security audit of DNS infrastructure
- Disaster recovery drill

**Annually:**
- Full DNS security assessment
- Update security policies
- Train team on new threats/defenses
