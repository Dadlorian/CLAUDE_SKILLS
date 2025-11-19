# DNS Architecture Patterns

## Hierarchical DNS Structure

### Root Name Servers
13 root nameserver clusters globally distributed (a-m.root-servers.net)
```
Query Flow:
Client -> Recursive Resolver -> Root Nameserver
                                    |
                                   TLD
                                    |
                            Authoritative Server
```

### TLD (Top-Level Domain) Servers
Managed by ICANN, route to authoritative servers
- `.com`, `.org`, `.net` (generic TLDs)
- `.uk`, `.de`, `.jp` (country-code TLDs)
- `.app`, `.dev`, `.cloud` (new gTLDs)

### Authoritative Nameservers
Hold actual DNS records for domain
- Primary (Master): Source of truth
- Secondary (Slave): Read-only copies via zone transfer
- Hidden Master: Not publicly listed in NS records

## Caching Hierarchy

### Full Resolver Stack
```
Client Application
       |
    Stub Resolver (OS resolver)
       |
Recursive Resolver (ISP/Public DNS)
       |
Root Nameserver (cached)
       |
TLD Nameserver (cached)
       |
Authoritative Nameserver (authoritative)
```

### Cache Timing
```
TTL Expiration Timeline:
- Query 1: example.com -> 3600 second TTL set
- Seconds 0-3599: Cached, served from recursive resolver
- Second 3600: TTL expires, query again when needed
- Multiple Queries: All served from cache within TTL window
```

### Cache Invalidation
```
Methods:
1. TTL Expiration: Automatic after TTL seconds
2. Resolver Cache Purge: BIND rndc flushname, Unbound control flush
3. Client Cache Clear: systemd-resolve --flush-caches, ipconfig /flushdns
4. Negative Cache: Caches NXDOMAIN for 300 seconds (typical)
```

## Anycast DNS Architecture

### Anycast Implementation
Multiple servers share same IP address, BGP announces from multiple locations
```
                    210.10.1.1
                    /    |    \
                   /     |     \
                  /      |      \
            Datacenter A  |  Datacenter B  Datacenter C
              (Region 1)  |  (Region 2)   (Region 3)

            Client in Region 1 -> Routed to nearest DC (A)
            Client in Region 2 -> Routed to nearest DC (B)
            Client in Region 3 -> Routed to nearest DC (C)
```

### Anycast Advantages
- Automatic geographic distribution
- Single IP address globally
- Reduced latency via routing proximity
- DDoS mitigation via distributed absorption
- Failover without DNS changes

### BGP Failover
```
If Datacenter A fails:
1. BGP session terminates
2. Announcement withdrawn from Region 1
3. Clients automatically route to next-nearest DC
4. No TTL waiting, immediate failover
```

## Split-Horizon DNS

### Architecture
Different DNS responses for internal vs. external clients
```
External Network (Internet)
└── DNS Query for internal.example.com
    └── Recursive Resolver (ISP/Public)
        └── Authoritative Server -> 203.0.113.1 (external IP)

Internal Network (Intranet)
└── DNS Query for internal.example.com
    └── Recursive Resolver (internal)
        └── Authoritative Server -> 10.0.0.1 (internal IP)
```

### Use Cases
- Separate internal and external service endpoints
- Reduce internal traffic to external networks
- Security isolation between zones
- Hybrid cloud architectures

### Implementation Patterns
```
Views in BIND:
zone "internal.example.com" {
    match-clients { internal-network; };
    file "zones/internal.example.com.internal";
};

zone "internal.example.com" {
    match-clients { external-network; };
    file "zones/internal.example.com.external";
};
```

## Geo-DNS Routing

### Geolocation Database
```
IP → GeoIP Lookup → Location → DNS Response

Client IP 203.0.113.5 (USA West)
    |
GeoIP Database lookup
    |
Returns location (California, USA)
    |
DNS Response: west-cdn.example.com (192.0.2.10)
```

### GeoDNS Patterns

#### Proximity-Based
```
Query from New York -> 192.0.2.1 (NYC endpoint)
Query from London  -> 192.0.2.2 (London endpoint)
Query from Tokyo   -> 192.0.2.3 (Tokyo endpoint)
```

#### Region-Based
```
Query from USA    -> cdn.us.example.com
Query from Europe -> cdn.eu.example.com
Query from APAC   -> cdn.apac.example.com
```

#### Load Balancing
```
All USA traffic -> 3 endpoints with weights:
- 50% -> East Coast
- 30% -> Central
- 20% -> West Coast
```

## Multi-Master Replication

### Master-Slave (Primary-Secondary)
```
Primary (Master)
    |
    | AXFR/IXFR Zone Transfer
    |
Secondary (Slave)
    | SOA Serial check every "Refresh" seconds
    | If primary serial > secondary serial, fetch new zone
```

### Multi-Master (Peer Replication)
```
Master A <--> Master B <--> Master C
(all read-write)

All masters accept updates via:
- nsupdate (RFC 2136)
- API calls
- Database replication

Synchronization via:
- DNS NOTIFY messages
- IXFR incremental transfers
- Database-level replication (PostgreSQL, MySQL)
```

### Zone Transfer Methods
```
AXFR (Full Zone Transfer):
1. Server initiates TCP connection to primary
2. Primary sends entire zone data
3. Secondary verifies, updates local file/database

IXFR (Incremental Zone Transfer):
1. Secondary sends SOA serial number
2. Primary sends only changed records (deltas)
3. Faster for large zones with small changes
```

## DNS Failover Patterns

### Health-Check Based Failover
```
Health Checker
    |
    | Probes: TCP/UDP/HTTP/HTTPS
    |
Primary DNS (192.0.2.1)
    ^ Healthy -> Return in DNS response
    | Unhealthy -> Remove from DNS response
    |
Secondary DNS (192.0.2.2)
```

### Configuration
```
SOA Authority Section:
- Primary responsible server
- Secondary responsible server

Health check determines which is returned:
If Primary DOWN: Only Secondary in responses
If Primary UP: Both in round-robin or weighted
```

### Client Failover
```
Client receives multiple A records:
192.0.2.1 (Primary - health check healthy)
192.0.2.2 (Secondary - fallback)

If Primary connection fails:
→ Client retries with Secondary IP
→ Application reconnects automatically
```

## Recursive Resolver Architecture

### Public Recursive Resolvers
```
Comparison:
Google (8.8.8.8):        - Global infrastructure, fast
Cloudflare (1.1.1.1):    - Privacy-first, privacy-friendly
Quad9 (9.9.9.9):         - Security-focused, blocks malware
OpenDNS (208.67.222.123): - Content filtering options
```

### Caching Strategy
```
Time Decay:
1. First query: Recursive lookup (100-500ms)
2. Queries within TTL: Cached response (<10ms)
3. After TTL: Repeat lookup

Cache Hit Ratio:
- Well-configured resolver: 95%+ hit rate
- Frequent TTL expirations: 60-70% hit rate
- Shared resolver (ISP): 90%+ due to shared cache
```

### Query Chains
```
Full query chain with depth tracking:
1. Client -> Recursive Resolver (Iteration 1)
2. Recursive Resolver -> Root (Iteration 2)
3. Root Response: Try .com TLD (Iteration 3)
4. TLD Response: Try authoritative ns1.example.com (Iteration 4)
5. Authoritative Response: Final answer (Iteration 5)

Result cached at each level for TTL duration
```

## DNS Security Patterns

### Query Authentication
```
DNSSEC Validation:
1. Request signed with RRSIG records
2. Recursive resolver verifies signature
3. Chain of trust validated to root KSK
4. BOGUS -> Dropped
5. SECURE -> Cached and returned
```

### Rate Limiting
```
DNS Amplification Protection:
- Limit responses to non-recursive queries
- Rate-limit responses per source IP
- Drop queries from bogus sources

Example:
rate-limit {
    responses-per-second 10;
    nxdomain-per-second 5;
};
```

### Query Logging
```
Log DNS queries for:
- Security analysis
- Performance debugging
- Compliance requirements

Log Fields:
- Timestamp
- Client IP
- Query domain
- Record type
- Response code
- Response time
```

## Hybrid Cloud DNS

### Hybrid Architecture
```
On-Premises Network
    |
    | DNS view: internal.example.com -> 10.0.0.x
    |
Hybrid Resolver (on-prem + cloud)
    |
    | Conditional forwarding to cloud DNS
    |
Cloud Network
    |
    | DNS view: cloud-services -> 10.1.0.x
```

### Conditional Forwarding
```
Rules:
- *.example.com -> On-premises DNS
- *.cloud.example.com -> Cloud DNS
- Default -> Public DNS resolution

Benefits:
- Seamless service discovery
- On-prem resources visible to cloud
- Cloud resources visible to on-prem
- Single DNS namespace
