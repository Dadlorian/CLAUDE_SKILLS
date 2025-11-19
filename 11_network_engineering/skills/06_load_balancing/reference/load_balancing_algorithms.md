# Load Balancing Algorithms Reference

## Overview
Load balancing algorithms determine how incoming requests are distributed across backend servers. Each algorithm has different characteristics, performance profiles, and use cases.

## L4 (Connection-level) Algorithms

### Round Robin
**Description**: Distributes connections sequentially to each backend server.

**Characteristics**:
- Simple and predictable
- No state tracking required
- Equal distribution (if all servers are equal)
- Ignores server capacity

**Use Cases**:
- Identical backend servers
- Quick deployment scenarios
- When complexity is not a factor

**Algorithm**:
```
current_index = (current_index + 1) % backend_count
select backend[current_index]
```

### Weighted Round Robin
**Description**: Distributes connections based on assigned weights to each backend.

**Characteristics**:
- Capacity-aware distribution
- Manual weight assignment
- More complex state tracking
- Better resource utilization

**Use Cases**:
- Heterogeneous server capacity
- Gradual traffic migration
- Testing new servers (low weight)

**Example Distribution**:
- Server A (weight 3): 60% of traffic
- Server B (weight 2): 40% of traffic

### Least Connections
**Description**: Sends new connections to the server with the fewest active connections.

**Characteristics**:
- Dynamic load balancing
- Handles variable connection times
- Continuous state tracking
- Better for long-lived connections

**Use Cases**:
- Database connections
- WebSocket connections
- Long-polling applications
- Heterogeneous server capacity

### Weighted Least Connections
**Description**: Least connections algorithm with server weights.

**Characteristics**:
- Dynamic with capacity awareness
- Combines least connections + weights
- More complex calculation
- Best for mixed server capacity

**Calculation**:
```
connection_ratio = active_connections / server_weight
select server with lowest connection_ratio
```

### IP Hash (Source Hash)
**Description**: Uses source IP address to consistently map to a backend server.

**Characteristics**:
- Stateless (no server state needed)
- Consistent (same client always hits same server)
- Hash collision handling required
- Good for session affinity

**Use Cases**:
- Session persistence
- Client-specific state
- Reducing memory usage on clients
- TCP connection reuse

**Algorithm**:
```
hash_value = hash(client_ip) % backend_count
select backend[hash_value]
```

### URI Hash
**Description**: Uses the URI/URL to consistently map to a backend server.

**Characteristics**:
- Good for content-based routing
- Enables caching optimization
- Consistent for same resource
- Useful for cache locality

**Use Cases**:
- Content caching
- Database sharding
- Resource-specific routing
- Cache coherency

### Random
**Description**: Randomly selects a backend server.

**Characteristics**:
- No state tracking
- Probabilistic distribution
- Works well with many backends
- Simple implementation

**Use Cases**:
- Simple scenarios
- Large number of backends
- Stateless services

### Least Response Time
**Description**: Selects server with lowest average response time plus active connections.

**Characteristics**:
- Performance-aware
- Requires metrics collection
- More complex calculation
- Adapts to server performance

**Formula**:
```
score = average_response_time + (active_connections / 10)
select server with lowest score
```

## L7 (Application-level) Algorithms

### HTTP Header-based Routing
**Description**: Routes based on HTTP headers.

**Common Headers**:
- `Host`: Domain-based routing
- `User-Agent`: Browser or client type
- `X-Forwarded-For`: Original client IP
- Custom headers: Application-specific routing

**Use Cases**:
- Multi-tenant applications
- API versioning
- Browser-specific content

### Cookie-based Routing
**Description**: Routes based on HTTP cookie values.

**Characteristics**:
- Requires cookie parsing
- Session affinity
- Can be client-manipulated
- Good for web applications

**Use Cases**:
- Session persistence
- A/B testing with client identifier
- User group routing

### URL Path-based Routing
**Description**: Routes based on URI path components.

**Example Routes**:
```
/api/* → API Backend
/static/* → Static Content Server
/admin/* → Admin Backend
/uploads/* → File Server
```

**Use Cases**:
- Microservices routing
- Service separation
- Content type separation

### Query Parameter Routing
**Description**: Routes based on URL query parameters.

**Use Cases**:
- Feature flag routing
- A/B testing parameters
- Client type routing

### Method-based Routing
**Description**: Routes based on HTTP method (GET, POST, PUT, etc.).

**Use Cases**:
- Separate read/write backends
- API endpoint routing
- Request type optimization

### Content-Type Routing
**Description**: Routes based on request or response Content-Type header.

**Use Cases**:
- JSON vs XML endpoints
- Media type handling
- Format-specific processing

## Advanced Algorithms

### Consistent Hashing
**Description**: Maps keys to a virtual ring for resilient distribution.

**Characteristics**:
- Minimal redistribution on server change
- Better for cache locality
- Complex implementation
- Used in distributed caching

**Advantages**:
- When one backend fails, only 1/n requests redirect
- Handles server addition/removal gracefully

### Weighted Round Robin with Dynamic Adjustment
**Description**: Adjusts weights based on real-time performance metrics.

**Metrics Used**:
- Response time
- Error rates
- CPU usage
- Custom health metrics

**Use Cases**:
- Adaptive load balancing
- Performance-based routing
- Load shedding scenarios

### Power of Two Choices
**Description**: Randomly selects two servers and chooses the one with fewer connections.

**Characteristics**:
- Near-optimal distribution
- Low computation overhead
- Better than pure random
- Less state than least connections

**Use Cases**:
- High-performance scenarios
- Distributed load balancing

## Algorithm Selection Matrix

| Algorithm | State | Fairness | Dynamic | Affinity | Complexity |
|-----------|-------|----------|---------|----------|------------|
| Round Robin | No | Good | No | No | Low |
| Weighted RR | No | Good | No | No | Low |
| Least Conn | Yes | Very Good | Yes | No | Medium |
| Weighted LC | Yes | Very Good | Yes | No | Medium |
| IP Hash | No | Fair | No | Yes | Low |
| Random | No | Fair | No | No | Low |
| Response Time | Yes | Excellent | Yes | No | High |
| Header-based | Yes | Variable | No | Optional | High |

## Performance Characteristics

### Throughput vs Latency
- **Throughput-optimized**: Round Robin, Random
- **Latency-optimized**: Least Connections, Response Time
- **Balanced**: Weighted Round Robin

### CPU Usage on Load Balancer
- **Low**: Round Robin, IP Hash, Random
- **Medium**: Least Connections, Weighted variants
- **High**: Response Time, Consistent Hashing, Header-based

### Memory Usage
- **Minimal**: Stateless algorithms (RR, Hash)
- **Moderate**: Least Connections
- **Significant**: Application-level tracking

## Recommendations by Use Case

### Web Applications
- **Primary**: Least Connections or Response Time
- **Fallback**: Weighted Round Robin
- **Session**: Cookie-based or IP Hash

### API Services
- **Primary**: Least Connections
- **Advanced**: Header/Path-based routing
- **Optimization**: Response Time based

### Database Services
- **Primary**: IP Hash or Weighted LC
- **Persistence**: Ensure same backend per client
- **Note**: Consider connection pooling

### Real-time Applications
- **Primary**: Least Connections
- **Advanced**: Custom metrics-based
- **Persistence**: Cookie or IP hash

### File Services
- **Primary**: URI Hash (cache locality)
- **Fallback**: IP Hash
- **Optimization**: Disk I/O considerations

---

**Last Updated**: 2025-11-19
**Version**: 2.0
