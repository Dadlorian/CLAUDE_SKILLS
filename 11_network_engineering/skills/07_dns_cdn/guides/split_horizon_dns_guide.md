# Split Horizon DNS Guide

## Overview

Split Horizon DNS returns different DNS responses based on query source:
- **Internal network**: Returns internal IP addresses
- **External network**: Returns external/public IP addresses
- **Hybrid setup**: On-prem users see on-prem services, cloud users see cloud services

## Architecture

```
┌──────────────────────────────────────────────────────┐
│              Internet (External)                      │
└──────────────────┬───────────────────────────────────┘
                   │
┌──────────────────▼────────────────────────────────┐
│      Authoritative DNS Server (Split Horizon)     │
├─────────────────────────────────────────────────┤
│  Query from external IP?                         │
│    ↓ Return public IP: 203.0.113.1             │
│  Query from internal IP?                         │
│    ↓ Return internal IP: 10.0.0.1              │
└──────────────────┬────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
    Internal            External
    Network             Network
    10.0.0.0/8         203.0.113.0/24
```

## Use Cases

### 1. Hybrid Cloud Architecture

```
On-Premises:
  - Employees, internal servers
  - database.example.com -> 10.0.0.50 (internal)

Cloud:
  - Cloud applications, microservices
  - api.example.com -> 203.0.113.100 (cloud)

Internal employee query:
  dig database.example.com -> 10.0.0.50 ✓ (internal)
  dig api.example.com -> 10.0.1.100 ✓ (hybrid cloud)

External cloud query:
  dig database.example.com -> ? (blocked/no access)
  dig api.example.com -> 203.0.113.100 ✓ (public cloud)
```

### 2. Service Separation

```
Scenario: Multiple environments (dev, staging, prod)

Internal query:
  example.com -> 10.0.0.10 (internal staging)
  Users test internal version before going public

External query:
  example.com -> 203.0.113.10 (production)
  Customers see production version
```

### 3. Load Balancing Separation

```
Internal traffic:
  api.example.com -> [10.0.1.1, 10.0.1.2] (internal LB)
  Stays within data center (faster)

External traffic:
  api.example.com -> [203.0.113.1, 203.0.113.2] (external LB)
  Routed through internet (but public IPs)
```

### 4. Security / Access Control

```
Sensitive services only accessible internally:
  internal.example.com -> 10.0.0.100
  External queries: NXDOMAIN (doesn't exist)

Public services:
  www.example.com -> 203.0.113.100
  All queries return public IP
```

## Implementation with BIND

### Step 1: Create ACLs

Define which networks are internal vs external:

```
// /etc/bind/named.conf

// Define internal networks
acl internal-networks {
  192.168.0.0/16;      // Corporate network
  10.0.0.0/8;          // Data center
  203.0.113.50/32;     // Hybrid resolver
  localhost;
};

acl external-networks {
  !internal-networks;  // Everything else
  any;
};
```

### Step 2: Create Views

Create separate DNS views for internal and external:

```
// Internal view (for internal-networks)
view "internal" {
  match-clients { internal-networks; };

  // Use local zone file with internal IPs
  zone "example.com" {
    type master;
    file "/etc/bind/zones/db.example.com.internal";
  };

  zone "0.0.10.in-addr.arpa" {
    type master;
    file "/etc/bind/zones/db.10.0.0";
  };

  // Forward unknown queries to root
  zone "." {
    type hint;
    file "/etc/bind/db.root";
  };
};

// External view (for external-networks)
view "external" {
  match-clients { external-networks; };

  // Use public zone file with public IPs
  zone "example.com" {
    type master;
    file "/etc/bind/zones/db.example.com.external";
  };

  // Forward unknown queries to root
  zone "." {
    type hint;
    file "/etc/bind/db.root";
  };
};
```

### Step 3: Create Zone Files

**Internal zone file** (/etc/bind/zones/db.example.com.internal):

```
$TTL 3600
$ORIGIN example.com.

@    IN    SOA    ns1.example.com. admin.example.com. (
           2024111901
           3600
           1800
           604800
           86400 )

@    IN    NS     ns1.example.com.
@    IN    NS     ns2.example.com.

ns1  IN    A      10.0.0.1    ; Internal NS
ns2  IN    A      10.0.0.2    ; Internal NS

; Internal services
@            IN    A      10.0.0.10         ; Internal IP
www          IN    A      10.0.0.10         ; Internal IP
api          IN    A      10.0.1.20         ; Internal API server
database     IN    A      10.0.0.50         ; Internal DB
internal-app IN    A      10.0.2.30         ; Sensitive internal
mail         IN    A      10.0.0.100        ; Internal mail
```

**External zone file** (/etc/bind/zones/db.example.com.external):

```
$TTL 3600
$ORIGIN example.com.

@    IN    SOA    ns1.example.com. admin.example.com. (
           2024111901
           3600
           1800
           604800
           86400 )

@    IN    NS     ns1.example.com.
@    IN    NS     ns2.example.com.

ns1  IN    A      203.0.113.1    ; Public NS
ns2  IN    A      203.0.113.2    ; Public NS

; Public services
@       IN    A      203.0.113.10    ; Public IP
www     IN    A      203.0.113.10    ; Public IP
api     IN    A      203.0.113.20    ; Public API

; Sensitive internal services not listed (hidden)
; internal-app: Not in external zone (inaccessible)
; database: Not in external zone (inaccessible)

; Mail server (may be public or internal)
mail    IN    A      203.0.113.100   ; Public mail relay
```

### Step 4: Set Permissions

```bash
sudo chown bind:bind /etc/bind/zones/db.example.com.*
sudo chmod 644 /etc/bind/zones/db.example.com.*
```

### Step 5: Reload BIND

```bash
sudo rndc reload

# Verify views loaded
sudo rndc status

# Check logs
tail -f /var/log/syslog | grep named
```

## Testing Split Horizon DNS

### Test from Internal Network

```bash
# Query from internal client (10.0.1.5)
dig @ns1.example.com api.example.com A

# Expected response:
# api.example.com.    3600    IN    A    10.0.1.20  (internal)

# Query sensitive internal record
dig @ns1.example.com internal-app.example.com A

# Expected response:
# internal-app.example.com. 3600 IN A 10.0.2.30  (accessible internally)
```

### Test from External Network

```bash
# Query from external client (203.0.113.50)
dig @ns1.example.com api.example.com A

# Expected response:
# api.example.com.    3600    IN    A    203.0.113.20  (public)

# Query sensitive internal record
dig @ns1.example.com internal-app.example.com A

# Expected response:
# ; (NXDOMAIN - doesn't exist for external clients)
```

### Simulate from Local Machine

```bash
# Query as if from internal network
dig @localhost internal-app.example.com A -b 127.0.0.1

# Query as if from external network
dig @localhost api.example.com A -b 127.0.0.1
```

## Hybrid Cloud Pattern

### Scenario: AWS Hybrid Setup

```
On-Prem:
- Windows Server with Active Directory
- Employees: 192.168.0.0/16
- Services:
  - internal.example.com -> 192.168.1.100
  - fileserver.example.com -> 192.168.1.200

AWS Cloud:
- EC2 instances, RDS, etc.
- Cloud subnets: 10.0.0.0/8
- Services:
  - api.example.com -> 10.0.1.20 (internal)
  - web.example.com -> 203.0.113.10 (public)

Hybrid Resolver:
- Sits at border between networks
- Internal view: resolves both on-prem + cloud internal
- External view: resolves only public records
```

### BIND Configuration

```
// Hybrid resolver config

acl on-prem {
  192.168.0.0/16;     // On-prem employees
  192.168.1.1;        // On-prem router
};

acl cloud-internal {
  10.0.0.0/8;         // AWS cloud
  203.0.113.100/32;   // Hybrid resolver itself
};

acl internal-sources {
  on-prem;
  cloud-internal;
};

acl external-sources {
  !internal-sources;
};

// Internal view (on-prem + cloud internal)
view "internal" {
  match-clients { internal-sources; };

  // Authoritative for example.com
  zone "example.com" {
    type master;
    file "/etc/bind/zones/db.example.com.internal";
  };

  // Forward to on-prem AD DNS for AD-specific records
  zone "corp.example.com" {
    type forward;
    forward-policy only;
    forwarders { 192.168.1.10; };  // On-prem DNS
  };

  // Root hints for unknown queries
  zone "." {
    type hint;
    file "/etc/bind/db.root";
  };
};

// External view (public only)
view "external" {
  match-clients { external-sources; };

  zone "example.com" {
    type master;
    file "/etc/bind/zones/db.example.com.external";
  };

  zone "." {
    type hint;
    file "/etc/bind/db.root";
  };
};
```

### Conditional Forwarding for AD Integration

```
// Forward corporate AD queries to AD DNS
zone "corp.example.com" {
  type forward;
  forward-policy only;
  forwarders {
    192.168.1.10;     // AD DNS server 1
    192.168.1.11;     // AD DNS server 2
  };
};

// Used by:
// - Internal clients querying AD domain
// - Cloud instances accessing on-prem resources
```

## Common Pitfalls

### Issue 1: DNS View Order Matters

```
// WRONG: Most specific first, then generic
view "internal" {
  match-clients { localhost; };
  // ... zones ...
};

view "external" {
  match-clients { any; };
  // ... zones ...
};

// This means localhost matches "internal" first ✓
// But if order reversed, localhost matches "external" first ✗

// RIGHT: Most specific first, always
view "internal" {
  match-clients { 192.168.0.0/16; 10.0.0.0/8; };
};

view "external" {
  match-clients { any; };  // Most generic, last
};
```

### Issue 2: Incomplete Zone Files

```
// Wrong: External zone doesn't resolve API
api.example.com  // Not in external zone file
// Results: NXDOMAIN for external queries (correct for sensitive)
// But breaks public API access

// Right: Public services in external zone
api.example.com    IN    A    203.0.113.20
www.example.com    IN    A    203.0.113.10

// Sensitive services NOT in external zone
// (internal-app.example.com not listed)
```

### Issue 3: Recursive Queries in Authoritative Views

```
// Problem: External view doesn't have recursion
// If external client queries unknown domain

// Solution: Add root hints to external view
view "external" {
  zone "." {
    type hint;
    file "/etc/bind/db.root";
  };

  // Or forward to public resolver
  forwarders { 8.8.8.8; };
};
```

## Monitoring Split Horizon DNS

### Verify Both Views Responding

```bash
#!/bin/bash
# Test both views

# Simulate internal query
echo "=== Internal View ==="
dig @127.0.0.1 -b 10.0.0.1 internal-app.example.com +short

# Simulate external query
echo "=== External View ==="
dig @127.0.0.1 -b 8.8.8.8 internal-app.example.com +short
```

### Monitor View Statistics

```bash
# Check which view served query
rndc stats

# Output in /var/named/named.stats:
# +++ Statistics Dump +++ (timestamp)
# ... per-view statistics ...
```

## Best Practices

1. **Clear Documentation**: Map which records appear in which views
2. **Consistent Naming**: Use clear prefixes (internal-, private-, etc.) or separate domains
3. **Test Thoroughly**: Query from both internal and external networks
4. **Monitor Separately**: Track query counts per view
5. **Backup Both Zones**: Keep both zone files in version control
6. **Security**: Restrict view access with ACLs
7. **Failover**: Ensure both views have redundant nameservers
8. **TTL Strategy**: May differ between views

## Troubleshooting

### Issue: View Not Matching Correctly

```bash
# Check which view matched
tail -f /var/log/syslog | grep "view"

# Verify ACL definitions
rndc dumpdb -all | grep "acl"

# Test ACL
nslookup -debug example.com
```

### Issue: Record Not Appearing

```bash
# Validate zone file
named-checkzone example.com /etc/bind/zones/db.example.com.internal
named-checkzone example.com /etc/bind/zones/db.example.com.external

# Check view configuration
grep -A 10 "view" /etc/bind/named.conf
```
