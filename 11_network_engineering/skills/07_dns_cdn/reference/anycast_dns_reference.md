# Anycast DNS Reference

## Anycast Fundamentals

### Definition
Multiple servers share the same IP address. Routing directs clients to the geographically nearest server via BGP.

### Anycast vs Unicast
```
Unicast:
One IP address = One server
1:1 mapping

Client in NYC -> 192.0.2.1 (NYC Server)
Client in LA  -> 192.0.2.2 (LA Server)
Client in EU  -> 192.0.2.3 (EU Server)

Multiple IPs needed for different locations

Anycast:
Multiple servers = Same IP address
Many-to-1 mapping

Client in NYC -> 192.0.2.1 -> Routes to nearest server (NYC)
Client in LA  -> 192.0.2.1 -> Routes to nearest server (LA)
Client in EU  -> 192.0.2.1 -> Routes to nearest server (EU)

Single IP, automatic routing to nearest
```

## Anycast DNS Architecture

### BGP Advertisement
```
DNS Server in NYC advertises:
192.0.2.1/32 via BGP to ISP

DNS Server in LA advertises:
192.0.2.1/32 via BGP to ISP

DNS Server in EU advertises:
192.0.2.1/32 via BGP to ISP

Result:
Client in NYC: Receives route to NYC server (shortest AS path)
Client in LA: Receives route to LA server (shortest AS path)
Client in EU: Receives route to EU server (shortest AS path)

Same IP, different destinations based on client location
```

### Path Selection
```
BGP selects best path based on:
1. AS Path length (shortest wins)
2. BGP local preference
3. Multi-exit discriminator (MED)
4. Neighbor BGP priority

NYC datacenter advertising 192.0.2.1:
- NYC ISP AS path: 1 (direct)
- Chosen by NYC clients (shortest path)

LA datacenter advertising 192.0.2.1:
- LA ISP AS path: 1 (direct)
- Chosen by LA clients (shortest path)

Internet routing automatically directs to nearest!
```

## DNS Root Nameserver Anycast

### 13 Root Servers
```
Official root nameservers (a-m.root-servers.net):
A: 198.41.0.4      (VeriSign, multiple locations)
B: 199.9.14.201    (ISC, multiple locations)
C: 192.33.4.12     (Cogent, multiple locations)
D: 199.7.91.13     (University of Maryland)
E: 192.203.230.10  (NASA)
F: 192.5.5.241     (Internet Systems Consortium)
G: 192.112.36.4    (University of Southern California)
H: 198.97.60.53    (U.S. Army Research Lab)
I: 192.36.148.17   (Netnod)
J: 192.58.128.30   (VeriSign)
K: 193.0.14.129    (RIPE NCC)
L: 199.7.83.42     (ICANN)
M: 202.12.27.33    (WIDE Project)

Each root server implements anycast:
Single IP (198.41.0.4) served from 100+ locations globally
```

### Root Anycast Implementation
```
AS Root-Servers (Private AS)

VeriSign hosts A root (198.41.0.4):
- USA locations: 5 sites (East, West, Central)
- Europe locations: 3 sites
- Asia locations: 4 sites
- Africa: 1 site
- South America: 1 site

All advertise 198.41.0.4 via BGP
Queries routed to nearest location automatically
```

### Query Flow
```
Client in Tokyo queries 198.41.0.4 (A root)
└─ BGP routes to WIDE Project location (nearest)
   └─ A root server responds from Tokyo
   └─ Extremely low latency (local!)

Client in London queries 198.41.0.4 (A root)
└─ BGP routes to RIPE NCC location (nearest)
   └─ A root server responds from London
   └─ Extremely low latency (local!)

Result: Millisecond latency to root nameserver globally!
```

## Implementing Anycast DNS

### Network Setup
```
Requirements:
- Multiple datacenters (geographically distributed)
- BGP connectivity to ISP/carrier
- Same IP address in all locations
- Identical DNS zone data
```

### Step 1: IP Address Planning
```
Obtain dedicated IP addresses:
- Dedicated /32 addresses for each nameserver
- Not under regular CIDR blocks
- Specifically for anycast

Example:
ns1.example.com anycast: 198.51.100.1 (shared by 3 DCs)
ns2.example.com anycast: 198.51.100.2 (shared by 3 DCs)

Register in DNS:
example.com.    3600    IN    NS    ns1.example.com.
example.com.    3600    IN    NS    ns2.example.com.
ns1.example.com 3600    IN    A     198.51.100.1
ns2.example.com 3600    IN    A     198.51.100.2
```

### Step 2: Configure Loopback Interface
```
Each datacenter configures loopback:

NYC Datacenter:
# ip addr add 198.51.100.1/32 dev lo

LA Datacenter:
# ip addr add 198.51.100.1/32 dev lo

EU Datacenter:
# ip addr add 198.51.100.1/32 dev lo

All three datacenters now have 198.51.100.1 configured
```

### Step 3: BGP Advertisement
```
NYC Datacenter (AS65001):
router bgp 65001
  neighbor 192.168.1.1 remote-as 65000  # NYC ISP
  !
  address-family ipv4
    network 198.51.100.1 mask 255.255.255.255
    neighbor 192.168.1.1 activate
  exit-address-family
!

LA Datacenter (AS65002):
router bgp 65002
  neighbor 192.168.2.1 remote-as 65000  # LA ISP
  !
  address-family ipv4
    network 198.51.100.1 mask 255.255.255.255
    neighbor 192.168.2.1 activate
  exit-address-family
!

EU Datacenter (AS65003):
router bgp 65003
  neighbor 192.168.3.1 remote-as 65000  # EU ISP
  !
  address-family ipv4
    network 198.51.100.1 mask 255.255.255.255
    neighbor 192.168.3.1 activate
  exit-address-family
!

All three announce 198.51.100.1
ISPs propagate to internet backbone
Clients route to nearest announcer
```

### Step 4: DNS Server Configuration
```
All three datacenters run identical DNS server with same zone data:

named.conf (BIND all locations):
zone "example.com" {
    type master;
    file "/etc/bind/zones/db.example.com";
    allow-transfer { 198.51.100.2; };  # Transfer to ns2
};

Zone data identical everywhere:
example.com     3600    SOA ns1.example.com. admin.example.com. (...)
example.com     3600    NS  ns1.example.com.
example.com     3600    NS  ns2.example.com.
www.example.com 3600    A   192.0.2.10

All datacenters serve identical responses!
```

### Step 5: Health Checking
```
Monitor DNS health at each location:

BIND health check script:
#!/bin/bash
# Query local DNS server
dig @127.0.0.1 example.com A

# If query fails:
# 1. Withdraw BGP announcement
# 2. Stop advertising 198.51.100.1
# 3. Alert operations

If queries succeed:
# 1. Advertise BGP
# 2. Accept traffic
# 3. Serve responses

Implementation (quagga):
router bgp 65001
  address-family ipv4
    neighbor 192.168.1.1 route-map health-check out
  exit-address-family
!

route-map health-check permit 10
  match ip address prefix-list anycast
  # Withdraw if DNS unhealthy (external health checker)
!
```

## Failover & Failure Modes

### Single Datacenters Fails
```
Before:
Client in NYC -> BGP route: NYC datacenters (shortest path)
Client in LA  -> BGP route: LA datacenters (shortest path)
Client in EU  -> BGP route: EU datacenters (shortest path)

NYC datacenters fail (DNS down, network down, etc.):
1. Health check fails
2. BGP announcement withdrawn
3. NYC traffic now routed to next-nearest (LA or EU)

Result: Traffic redirected within seconds!
No TTL waiting (not DNS change, BGP change)
```

### Network Path Failures
```
If NYC-ISP connection fails (but DNS still up):
1. BGP route through NYC withdrawn
2. NYC traffic reroutes through alternative path
3. May route to LA or EU (depends on BGP topology)

If all paths to NYC fail:
1. NYC DNS unreachable
2. Traffic routes to alternative datacenters
3. No anycast change needed
```

## Advantages

### 1. Latency Reduction
```
Traditional DNS:
Client in Tokyo -> Queries authoritative server in New York
└─ ~200ms latency

Anycast DNS:
Client in Tokyo -> Queries anycast (routed to Tokyo location)
└─ <10ms latency

Latency improvement: 95% reduction!
```

### 2. Automatic Failover
```
Datacenters fail → BGP updated → Traffic redirected
No DNS TTL waiting
No manual intervention
Millisecond-level failover
```

### 3. DDoS Absorption
```
Anycast distributes DDoS traffic across multiple locations:
Attacker target: ns1.example.com (198.51.100.1)

Without anycast:
All traffic → Single datacenter
Datacenter overwhelmed, goes down

With anycast:
Traffic distributed to nearest locations
Each location absorbs portion of attack
Distributed capacity resists larger attacks
```

### 4. Single IP for Multiple Locations
```
One IP address
Multiple datacenters
Simpler management
Simpler DNS records
```

## Challenges

### 1. Session Affinity
```
Problem: Same client might get different server per query

Query 1: Client routed to NYC server
Query 2: Client routed to LA server (different BGP path)
Both return same data (identical zones), but different server

For DNS: Not a problem (stateless)
For other protocols: Requires state synchronization
```

### 2. Zone Synchronization
```
Challenge: Keep all datacenters synchronized

Solution 1: Multi-master replication
- All masters read-write
- Database replication (MySQL, PostgreSQL)
- Real-time synchronization

Solution 2: Primary-secondary
- Primary (NYC) → Secondary (LA, EU)
- AXFR zone transfers
- ~5 minute lag possible

Solution 3: Shared storage
- NFS, S3, or other shared filesystem
- All datacenters mount same zone file
- Instant consistency
```

### 3. BGP Configuration Complexity
```
Requires BGP expertise:
- AS numbers
- Route maps
- Local preference
- MED values
- Community strings
- Health checking integration

Not simple for non-BGP networks
May require ISP cooperation
```

### 4. Anycast Routing Anomalies
```
Issues:
1. Asymmetric routing (request to NYC, response from LA)
2. BGP convergence delays (traffic blackhole during update)
3. Partial BGP withdrawals (some ISPs still routed to failed DC)

Mitigation:
1. Robust health checking
2. Conservative BGP timers
3. Monitoring and alerting
4. Regular failover testing
```

## Anycast DNS Best Practices

1. **Geographic Distribution**: Place datacenters >1000km apart
2. **Multiple ISPs**: Each datacenters on different ISP (diverse connectivity)
3. **Health Checking**: Aggressive checks (10 second intervals)
4. **Zone Synchronization**: Real-time replication preferred
5. **BGP Optimization**: Work with ISPs on routing
6. **Monitoring**: Alert on BGP route changes
7. **Testing**: Regular failover drills
8. **Documentation**: Map BGP configuration and troubleshooting
9. **Capacity Planning**: Each location must handle full load
10. **Compliance**: Verify ISP allows anycast announcements

## Tools & Implementation

### Quagga / FRR (Free Range Routing)
```
Open source BGP daemon
Commonly used for anycast

frr.conf:
router bgp 65000
  bgp router-id 192.168.1.1
  neighbor 192.168.1.1 remote-as 65000
  !
  address-family ipv4 unicast
    network 198.51.100.0/24
  exit-address-family
!
```

### Health Check Integration
```
Script to monitor and update BGP:

#!/bin/bash
while true; do
  if dig @127.0.0.1 example.com A +short > /dev/null; then
    # DNS is healthy, advertise
    vtysh -c "configure terminal" \
          -c "router bgp 65000" \
          -c "address-family ipv4" \
          -c "network 198.51.100.1/32"
  else
    # DNS is unhealthy, withdraw
    vtysh -c "configure terminal" \
          -c "router bgp 65000" \
          -c "address-family ipv4" \
          -c "no network 198.51.100.1/32"
    # Alert operations
    echo "DNS health check failed" | mail -s "Anycast failure" ops@example.com
  fi
  sleep 10
done
```

## Industry Examples

### Google Public DNS (8.8.8.8)
- Anycast across 100+ locations globally
- Sub-millisecond latency worldwide
- Distributed DDoS protection

### Cloudflare 1.1.1.1
- 200+ anycast locations
- Global latency < 50ms
- Privacy-focused resolver

### Quad9 (9.9.9.9)
- Anycast infrastructure
- Security-focused filtering
- Global distribution
