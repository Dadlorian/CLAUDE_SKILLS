# Layer 4 Load Balancing Guide

## Overview
Layer 4 (Transport Layer) load balancing distributes connections and traffic based on network-level information such as source/destination IP addresses and ports, without examining application content.

## When to Use L4 Load Balancing

### Ideal Use Cases
- **TCP Services**: Database connections, cache services, message queues
- **Non-HTTP Protocols**: MySQL, PostgreSQL, Redis, Memcached, RabbitMQ
- **UDP Services**: DNS, RADIUS, VoIP
- **Extreme Performance**: Maximum throughput, minimum latency
- **Stream Data**: Video/audio streaming, file transfer
- **Real-time Applications**: Gaming, trading platforms

### Not Suitable For
- HTTP/HTTPS applications (better with L7)
- Content-based routing
- Request manipulation
- Cookie-based affinity
- Multiple services on same port

## L4 vs L7 Comparison

| Aspect | L4 | L7 |
|--------|-----|-----|
| **Decision Point** | Connection 5-tuple | HTTP headers/content |
| **Visibility** | Network only | Application aware |
| **Performance** | Highest | Good |
| **Latency** | Lowest | Slightly higher |
| **State** | Minimal | Full request context |
| **Cost** | Lower | Higher |
| **Flexibility** | Limited | Extensive |
| **Setup Complexity** | Simple | Moderate |

## Architecture Design

### Single Tier L4 LB
```
                    Clients
                      │
              ┌───────┴────────┐
              │                │
          ┌───▼───┐        ┌───▼───┐
          │ Client │        │ Client │
          └───┬───┘        └───┬───┘
              │                │
              └────────┬───────┘
                       │
                   ┌───▼────┐
                   │   L4   │
                   │   LB   │
                   └───┬────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
      ┌──▼──┐      ┌──▼──┐      ┌──▼──┐
      │ BE1 │      │ BE2 │      │ BE3 │
      └─────┘      └─────┘      └─────┘

Configuration:
- Simple, straightforward
- No application-level decisions
- All connections treated equally
```

### Multi-Tier L4 LB (Frontend + Backend)
```
                  Clients
                    │
              ┌─────▼─────┐
              │  L4 LB #1  │ (Frontend)
              │ (Public IP)│
              └─────┬─────┘
                    │
         ┌──────────┼──────────┐
         │          │          │
      ┌──▼──┐   ┌──▼──┐   ┌──▼──┐
      │L4LB2│   │L4LB3│   │L4LB4│ (Backend tier)
      └──┬──┘   └──┬──┘   └──┬──┘
         │         │         │
    ┌────┴────┐ ┌──┴────┐ ┌──┴────┐
    │ Backend │ │Backend│ │Backend │
    │ Pool 1  │ │Pool 2 │ │Pool 3  │
    └─────────┘ └───────┘ └────────┘
```

## Protocol-Specific Configurations

### MySQL Load Balancing
**Characteristics**:
- Long-lived connections (minutes to hours)
- Stateful protocol
- Connection pooling expected
- Authentication per connection

**Configuration Example**:
```
Listener: Port 3306 (TCP)
Load Balancing: Source IP Hash
  (Ensures same client connects to same MySQL instance)

Pool Members:
  - mysql-primary: 192.168.1.10:3306
  - mysql-replica1: 192.168.1.11:3306
  - mysql-replica2: 192.168.1.12:3306

Health Check: TCP connection to port 3306
Timeout: 30 minutes (MySQL default)
Connection Limit: 500 per backend
```

**Why Source IP Hash?**:
- Maintains session state per client
- Client doesn't see connection switching
- Connection-specific authentication preserved
- Transaction consistency

### Redis Load Balancing
**Characteristics**:
- Key-based (logical) partitioning preferred
- Connection multiplexing
- In-memory data store
- Fast response times

**Configuration Example**:
```
Listener: Port 6379 (TCP)
Load Balancing: Source IP Hash
  (Clients connect to same Redis instance)

Pool Members:
  - redis-1: 192.168.1.20:6379
  - redis-2: 192.168.1.21:6379
  - redis-3: 192.168.1.22:6379

Health Check: TCP + PING command
Timeout: 5 seconds
Persistence: Source IP (sticky sessions)
```

**Advanced Approach** (Redis Cluster):
- Redis Cluster handles distribution internally
- Load balancer just distributes connections
- Clients see redirects to appropriate cluster members
- More complex but scalable

### PostgreSQL Load Balancing
**Characteristics**:
- Similar to MySQL
- Connection pooling expected
- Read replicas vs primary
- Middleware for read/write splitting

**Configuration Example**:
```
Listener: Port 5432 (TCP)
Strategy: Separate pools for read/write

Write Pool:
  - primary: 192.168.1.30:5432

Read Pool:
  - replica1: 192.168.1.31:5432
  - replica2: 192.168.1.32:5432
  - replica3: 192.168.1.33:5432

Load Balancing: Least connections
Health Check: TCP connection
```

**Application Integration**:
```
Write operations → Write pool (single primary)
Read operations → Read pool (multiple replicas)
Connection pooling on client side
```

### DNS Load Balancing (Port 53)
**Characteristics**:
- Short-lived UDP connections
- Stateless requests
- Simple and fast
- High throughput

**Configuration Example**:
```
Listener: Port 53 (UDP)
Load Balancing: Round Robin
  (Simple, each query goes to next server)

Pool Members:
  - dns1: 192.168.1.50:53
  - dns2: 192.168.1.51:53
  - dns3: 192.168.1.52:53
  - dns4: 192.168.1.53:53

Health Check: DNS query test
Timeout: 2 seconds
```

## Load Balancing Algorithm Selection

### For Database Services (Use Source IP Hash)
**Reason**: Maintains client-server affinity
```
┌─────────────────────────────────────┐
│ Client IP: 192.168.1.100           │
│ Hash(IP) % 3 = 1                   │
│ Always → Database Server 2         │
└─────────────────────────────────────┘
```

### For DNS/Cache (Use Round Robin)
**Reason**: Stateless, equal distribution
```
Query 1 → Server 1
Query 2 → Server 2
Query 3 → Server 3
Query 4 → Server 1 (repeat)
```

### For Connection Pooling (Use Least Connections)
**Reason**: Dynamic load awareness
```
Server 1: 50 connections
Server 2: 75 connections
Server 3: 40 connections
↓
New connection → Server 3 (fewest)
```

### For Mixed Capacity (Use Weighted Round Robin)
**Reason**: Capacity-aware distribution
```
Server 1 (2 CPU): weight = 2
Server 2 (4 CPU): weight = 4
Server 3 (2 CPU): weight = 2

Distribution:
  Server 1: 25% of traffic
  Server 2: 50% of traffic
  Server 3: 25% of traffic
```

## Health Checking for L4

### TCP Health Check
**Simple Connection Test**:
```
Interval: 5 seconds
Timeout: 3 seconds
Attempt to connect to TCP port

Success = Connection established
Failure = Connection refused/timeout
```

**Configuration**:
```
Monitor Type: TCP
Port: Service port (3306 for MySQL)
Interval: 5 seconds
Timeout: 3 seconds
Up Threshold: 2 consecutive passes
Down Threshold: 3 consecutive failures
```

### Advanced Health Check (Service Validation)
**Send/Expect Pattern**:
```
Send: PING command
Expect: PONG response

MySQL Example:
  Send: (custom script checking connectivity)
  Expect: Success response
```

## Connection Management

### Connection Timeout Configuration
**Idle Timeout**: Close inactive connections
```
Typical Value: 300 seconds (5 minutes)
Database: 1800 seconds (30 minutes)
Cache: 60 seconds (1 minute)

Setting:
  If no data transfer for X seconds → close connection
```

### Connection Limits
**Per Backend**:
```
Max Connections: 1000 per database server
    If limit reached:
      - New connections queue
      - Or rejected with error
      - Or routed to different server
```

**Per Load Balancer**:
```
Max Total: 100,000 connections
    Prevents resource exhaustion
    Protects infrastructure
```

## High Availability Configuration

### Active-Standby L4 LB Pair
```
┌────────────────────────────────────┐
│        Virtual IP (203.0.113.1)    │
└───────────┬────────────────────────┘
            │
     ┌──────┴─────────┐
     │ (heartbeat)    │
  ┌──▼───┐        ┌────▼──┐
  │ LB-1 │        │ LB-2  │
  │ Active│◄─────►│Standby│
  └──┬───┘        └───────┘
     │
  ┌──▼────────────────────┐
  │   Backend Services    │
  └──────────────────────┘
```

**Configuration**:
- Both LBs have same configuration
- Active LB owns virtual IP (via VRRP/keepalived)
- Standby LB monitors active
- Automatic failover on failure

### Active-Active L4 LB Setup
```
        Virtual IP (203.0.113.1)
                  │
        ┌─────────┴──────────┐
     ┌──▼───┐           ┌───▼──┐
     │ LB-1 │           │ LB-2 │
     │Active│           │Active│
     └──┬───┘           └──┬───┘
        │                  │
     ┌──▼──────────────────▼──┐
     │  Backend Services      │
     └────────────────────────┘
```

**Considerations**:
- Both handle traffic equally
- Session state must be external (shared storage)
- More complex than active-standby
- Better resource utilization

## Monitoring and Troubleshooting

### Key Metrics to Monitor
```
1. Connection Count
   - Current active connections
   - Connections per second (CPS)
   - Alert if exceeds threshold

2. Throughput
   - Bits per second
   - Packets per second
   - Alert on unusual changes

3. Backend Health
   - Number of healthy vs unhealthy
   - Health check response time
   - Alert on status changes

4. Latency
   - Average response time
   - P95/P99 latency
   - Alert on increases
```

### Common Issues and Solutions

**Issue: Unbalanced Load Distribution**
```
Symptom:
  Server 1: 1000 connections
  Server 2: 100 connections
  Server 3: 50 connections

Diagnosis:
  - Hash algorithm creating skew
  - Clients from limited IP range
  - Connection pooling concentration

Solution:
  - Switch to least connections
  - Review connection distribution
  - Load balance clients differently
```

**Issue: Connection Timeouts**
```
Symptom:
  Applications getting "Connection timeout" errors
  LB shows connection refused

Cause:
  - Backend server overloaded
  - Health check too strict
  - Network connectivity issue

Solution:
  - Check backend resource (CPU, memory, connections)
  - Verify health check is realistic
  - Check network path (ping, traceroute)
```

**Issue: Uneven Session Distribution (with IP Hash)**
```
Symptom:
  Some backends heavily loaded, others light

Cause:
  - Clients come from same network (same subnet)
  - NAT converting client IPs

Solution:
  - Use least connections instead of IP hash
  - Modify hash function (if available)
  - Load balance at different layer (DNS, proxy)
```

## Best Practices

1. **Use Appropriate Health Checks**
   - TCP check for raw connectivity
   - Application-level check for true health
   - Regular interval (5-10 seconds typical)

2. **Session Affinity**
   - Use IP hash for stateful services
   - Verify clients see persistent routing
   - Test failover behavior

3. **Connection Tuning**
   - Set appropriate timeouts
   - Monitor connection counts
   - Configure connection limits
   - Test connection pooling

4. **Monitoring**
   - Monitor all metrics (connections, throughput, health)
   - Set appropriate thresholds
   - Alert on anomalies
   - Track trends over time

5. **Testing**
   - Test failover (manual and automated)
   - Test connection exhaustion
   - Test health check failures
   - Test uneven load distribution

6. **Documentation**
   - Document pool composition
   - Document health check logic
   - Document timeout values
   - Document monitoring/alerting

---

**Last Updated**: 2025-11-19
**Version**: 2.0
