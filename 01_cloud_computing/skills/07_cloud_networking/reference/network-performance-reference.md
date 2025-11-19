# Network Performance Reference

## Introduction

Network performance optimization is critical for application responsiveness, user experience, and efficient resource utilization. This reference covers techniques, tools, and best practices for optimizing cloud network performance.

## Performance Metrics

### Key Metrics

**Latency**:
```
Round-Trip Time (RTT): Time for request + response
One-Way Latency: Time for packet to reach destination
Jitter: Variation in latency
Acceptable: < 100ms for interactive apps
Good: < 50ms
Excellent: < 20ms
```

**Bandwidth**:
```
Throughput: Actual data transfer rate
Available Bandwidth: Maximum theoretical rate
Utilization: Percentage of bandwidth in use
Units: Mbps, Gbps
```

**Packet Loss**:
```
Measurement: Percentage of packets lost
Acceptable: < 1%
Good: < 0.1%
Excellent: < 0.01%

Causes: Congestion, errors, resource limits
```

**Connection Metrics**:
```
Active Connections: Current open connections
Connection Rate: New connections per second
Connection Errors: Failed connection attempts
Connection Duration: Average connection lifetime
```

### Measurement Tools

**Network Testing**:
```bash
# Latency test
ping -c 10 example.com

# Trace route
traceroute example.com

# MTR (combined ping + traceroute)
mtr example.com

# Bandwidth test
iperf3 -c server-ip -t 30

# TCP connection test
nc -zv hostname port

# HTTP performance
curl -w "@curl-format.txt" -o /dev/null -s https://example.com
```

**Cloud Provider Tools**:
```
AWS:
- VPC Reachability Analyzer
- CloudWatch Network Metrics
- Network Insights

Azure:
- Network Watcher (Connection Monitor, Performance Monitor)
- Connection Troubleshoot
- Network Performance Monitor

GCP:
- Network Intelligence Center
- Connectivity Tests
- Performance Dashboard
```

## Latency Optimization

### Geographic Proximity

**Edge Locations**:
```
User Location --> Nearest Edge Location

CloudFront: 225+ locations
Azure CDN: 118+ locations
Cloud CDN: 90+ locations

Benefit: 20-60% latency reduction
```

**Regional Deployment**:
```
Deploy in regions closest to users:

US users --> us-east-1, us-west-2
EU users --> eu-west-1, eu-central-1
Asia users --> ap-southeast-1, ap-northeast-1

Multi-region active-active for global users
```

### AWS Global Accelerator

**Anycast Optimization**:
```
Traditional Path:
User --> ISP --> Public Internet --> AWS Region
Latency: 100-300ms

Global Accelerator Path:
User --> AWS Edge Location --> AWS Private Network --> AWS Region
Latency: 50-150ms

Improvement: 40-60% reduction
```

**Configuration**:
```
Static Anycast IPs: 2 IPs
Endpoints: ALB, NLB, EC2, EIP
Health Checks: Continuous monitoring
Failover: Automatic, < 30 seconds
Traffic Dials: Per-region traffic control
```

### DNS Resolution Time

**Reduce DNS Lookup Time**:
```
Strategies:
1. Use anycast DNS (Route 53, Cloud DNS)
2. Optimize TTL values
3. Prefetch DNS (dns-prefetch hint)
4. Minimize DNS lookups (fewer domains)
5. Use DNS caching at application level

DNS Lookup Time:
Good: < 20ms
Acceptable: < 100ms
Poor: > 100ms
```

### Connection Establishment

**TCP Handshake Optimization**:
```
Standard TCP Handshake (3-way):
SYN --> (30ms)
SYN-ACK <-- (30ms)
ACK --> (30ms)
Total: ~90ms + data transfer

TLS Handshake (TLS 1.2):
Additional 2 RTTs
Total: 90ms + 60ms = 150ms before data

TLS 1.3 (Optimized):
1 RTT for TLS
Total: 90ms + 30ms = 120ms before data
```

**Connection Reuse**:
```
HTTP Keep-Alive:
- Reuse TCP connections
- Eliminate handshake overhead
- Reduce latency by 50-100ms per request

HTTP/2:
- Single connection, multiple streams
- Multiplexing
- Header compression
- Further latency reduction
```

## Bandwidth Optimization

### Compression

**Content Compression**:
```
Gzip/Brotli Compression:
- Text files: 70-90% reduction
- HTML: 60-80% reduction
- JSON: 70-80% reduction
- CSS/JS: 60-70% reduction

Enable at:
- CDN (CloudFront, Azure CDN, Cloud CDN)
- Load Balancer (ALB)
- Web Server (nginx, Apache)
```

**Configuration Example** (nginx):
```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_comp_level 6;
gzip_types
    text/plain
    text/css
    text/javascript
    application/json
    application/javascript
    application/xml;
```

### Data Transfer Optimization

**S3 Transfer Acceleration**:
```
Traditional: User --> S3 bucket (public internet)
Accelerated: User --> CloudFront edge --> AWS backbone --> S3

Speed Improvement: 50-500%
Cost: Additional $0.04-$0.08 per GB
Use case: Large file uploads from distant locations
```

**Azure ExpressRoute**:
```
Direct connection to Azure
Bypass public internet
Consistent performance
Lower latency
Higher bandwidth

Speeds: 50 Mbps to 10 Gbps
```

**GCP Cloud Interconnect**:
```
Dedicated: 10 Gbps or 100 Gbps
Partner: 50 Mbps to 50 Gbps

Direct to Google network
Lower latency
Higher throughput
```

### Protocol Optimization

**HTTP/2 Benefits**:
```
Multiplexing: Multiple requests per connection
Header Compression: Reduce overhead
Server Push: Proactively send resources
Binary Protocol: More efficient parsing

Performance Improvement: 20-50%
```

**HTTP/3 (QUIC)**:
```
UDP-based transport
0-RTT connection establishment
Improved congestion control
Better mobile performance
Faster page loads: 10-30%

Supported: CloudFront, some CDNs
```

**TCP Tuning**:
```
TCP Window Scaling: Larger windows for high-bandwidth links
Selective Acknowledgment (SACK): Efficient retransmission
TCP Fast Open: Reduce connection latency
Congestion Control Algorithms: BBR, CUBIC
```

## Network Architecture Optimization

### VPC Design for Performance

**Availability Zone Awareness**:
```
Same AZ Deployment:
- Web tier AZ-1a
- App tier AZ-1a
- Cache AZ-1a
Benefit: Lower latency (< 1ms)
Risk: No AZ failover

Multi-AZ Deployment:
- Web tier AZ-1a, 1b
- App tier AZ-1a, 1b
- Cache AZ-1a, 1b (replication)
Benefit: High availability
Cost: Cross-AZ data transfer (AWS)
```

**Placement Groups** (AWS):
```
Cluster Placement Group:
- Single AZ
- Low latency (10 Gbps)
- HPC workloads

Partition Placement Group:
- Spread across partitions
- Large distributed systems (Hadoop, Cassandra)

Spread Placement Group:
- Distinct underlying hardware
- Critical instances
```

### VPC Endpoints

**AWS VPC Endpoints**:
```
Without Endpoint:
Instance --> NAT Gateway --> Internet --> S3
Latency: 50-100ms
Cost: NAT + data transfer

With Gateway Endpoint:
Instance --> VPC Endpoint --> S3
Latency: 5-10ms
Cost: Free for S3/DynamoDB

Benefits:
- 80-90% latency reduction
- No internet traversal
- No NAT bandwidth limit
- No data transfer charges
```

**Azure Private Link**:
```
Without Private Link:
VM --> Public Internet --> Azure SQL
Latency: 50ms

With Private Link:
VM --> Private Endpoint --> Azure SQL
Latency: 5ms

Benefit: 10x latency reduction
```

### Load Balancer Optimization

**Connection Pooling**:
```
Load Balancer Configuration:
- HTTP Keep-Alive: Enabled
- Idle Timeout: 60-300 seconds
- Connection Draining: 30-300 seconds

Backend Configuration:
- Max connections: Appropriate sizing
- Connection timeout: Match LB
- Keep-alive: Enabled
```

**Health Check Tuning**:
```
Interval: 5-30 seconds
Timeout: 2-10 seconds
Healthy Threshold: 2-5
Unhealthy Threshold: 2-5

Faster Intervals:
- Quicker failure detection
- More health check traffic
- Higher cost

Recommendation: 10-15 second interval
```

## CDN and Caching

### Cache Strategy

**Cache Control Headers**:
```
Static Assets (images, CSS, JS):
Cache-Control: public, max-age=31536000, immutable
(1 year, with versioning)

Dynamic API Responses:
Cache-Control: private, max-age=300
(5 minutes, user-specific)

Frequently Updated:
Cache-Control: public, max-age=60, must-revalidate
(1 minute, validate before serving stale)

No Cache:
Cache-Control: no-store, no-cache
(Never cache)
```

**Cache Hit Ratio**:
```
Target: > 85%
Good: > 90%
Excellent: > 95%

Improvement Strategies:
- Increase TTL where appropriate
- Normalize cache keys
- Pre-warm cache
- Remove unnecessary query parameters
- Use versioned URLs for static assets
```

### Edge Computing

**Lambda@Edge Use Cases**:
```
Performance Improvements:
- A/B testing at edge
- Image optimization
- Device detection and adaptive content
- Geo-based content
- SEO optimization

Latency Reduction: 50-200ms
```

**CloudFront Functions**:
```
Microsecond Execution:
- URL rewrites
- Header manipulation
- Cache key normalization

Cost: 1/6 of Lambda@Edge
Latency: < 1ms
```

## Database Performance

### Connection Pooling

**RDS Proxy**:
```
Without Proxy:
Lambda --> Direct RDS Connection
- Each Lambda = New connection
- Connection overhead
- Limited connections

With RDS Proxy:
Lambda --> RDS Proxy --> RDS
- Connection pooling
- Reduced connection overhead
- Handle thousands of Lambdas
- Failover support

Latency Reduction: 20-40ms per request
```

**Application-Level Pooling**:
```
Configuration:
- Min connections: 5-10
- Max connections: 20-50
- Idle timeout: 5-10 minutes
- Connection lifetime: 30-60 minutes

Benefits:
- Reuse connections
- Faster queries
- Reduced database load
```

### Read Replicas

**Read Scaling**:
```
Primary (Writes):
- us-east-1a

Read Replicas (Reads):
- us-east-1a (same AZ)
- us-east-1b (different AZ)
- eu-west-1 (different region)

Route read traffic to:
- Same-AZ replica (< 1ms latency)
- Cross-AZ replica (1-5ms latency)
- Cross-region replica (50-200ms latency)
```

### Caching Layer

**ElastiCache/Redis**:
```
Cache Hit:
App --> ElastiCache --> Return (< 1ms)

Cache Miss:
App --> ElastiCache --> Database --> Return (~50ms)
     --> Cache for next request

Cache Hit Ratio: Target > 90%
Latency Reduction: 98% (50ms to 1ms)
```

**DynamoDB DAX**:
```
Without DAX:
App --> DynamoDB (~10ms)

With DAX:
App --> DAX --> DynamoDB (cache miss)
App --> DAX (cache hit) (~1ms)

Microsecond latency
10x performance improvement
```

## Monitoring and Profiling

### Application Performance Monitoring

**Distributed Tracing**:
```
End-to-End Request Trace:
1. User Request: 0ms
2. CloudFront: 20ms
3. ALB: 5ms
4. Application: 50ms
   - Database Query: 30ms
   - External API: 15ms
   - Processing: 5ms
5. Response: 75ms total

Identify bottlenecks
Optimize slow components
```

**Network Metrics**:
```
CloudWatch Metrics:
- Network In/Out
- Packet Loss
- Connection Count
- Latency (ALB Target Response Time)

Azure Monitor:
- Network In/Out
- Connections
- Response Time

GCP Cloud Monitoring:
- Network throughput
- Packet loss
- RTT latency
```

### VPC Flow Logs Analysis

**Performance Analysis**:
```
High Packet Count, Low Bytes:
- Small packets (inefficient)
- Many connections
- Potential optimization

High Reject Count:
- Security group/NACL blocking
- Application not listening
- Check configuration

Long Connection Duration:
- Connection leaks
- Missing timeouts
- Review application
```

### Synthetic Monitoring

**External Monitoring**:
```
CloudWatch Synthetics:
- Canary scripts
- Check endpoints globally
- Measure latency from different regions
- Alert on degradation

Azure Application Insights:
- Availability tests
- Multi-region testing
- Performance tracking

GCP Cloud Monitoring:
- Uptime checks
- Latency monitoring
```

## Advanced Optimization Techniques

### Jumbo Frames

**MTU Optimization**:
```
Standard MTU: 1500 bytes
Jumbo Frames: 9000 bytes

Benefit: Reduced CPU overhead, higher throughput
Use case: Intra-VPC, high-bandwidth transfers

AWS: Supported within VPC
Azure: Supported within VNet
GCP: Supported within VPC
```

### TCP Window Scaling

**High-Bandwidth Optimization**:
```
Bandwidth-Delay Product:
BDP = Bandwidth × RTT

Example:
1 Gbps × 50ms = 6.25 MB
Need TCP window > 6.25 MB for full utilization

Enable Window Scaling:
Linux: Default enabled
TCP window: Up to 1 GB (theoretically)
```

### Multipath TCP

**Connection Aggregation**:
```
Multiple network paths simultaneously
Increased throughput
Improved reliability
Mobile/WiFi handoff

Support: Limited, improving
```

### Enhanced Networking

**AWS Enhanced Networking**:
```
Elastic Network Adapter (ENA):
- Up to 100 Gbps
- Low latency
- High PPS (packets per second)
- SR-IOV

Requirement: Supported instance types (C5, M5, R5, etc.)
```

**Azure Accelerated Networking**:
```
SR-IOV to bypass host networking
Lower latency
Higher throughput
Reduced CPU

Supported: Most VM sizes
```

**GCP Virtio**:
```
Default on all instances
Optimized virtio drivers
Low overhead
High performance
```

## Best Practices

### Design

1. Deploy close to users (multi-region if global)
2. Use CDN for static and dynamic content
3. Implement caching at every layer
4. Choose appropriate instance types and sizes
5. Use VPC endpoints for cloud services
6. Enable enhanced networking
7. Design for connection reuse

### Configuration

1. Enable compression (gzip/Brotli)
2. Configure HTTP Keep-Alive
3. Use HTTP/2 or HTTP/3
4. Optimize DNS (low TTL for changes, high for stable)
5. Tune TCP parameters for workload
6. Configure appropriate timeouts
7. Use connection pooling

### Monitoring

1. Track latency (p50, p95, p99)
2. Monitor bandwidth utilization
3. Watch connection counts
4. Set up distributed tracing
5. Alert on performance degradation
6. Regular performance testing
7. Analyze VPC flow logs

### Optimization

1. Profile application for bottlenecks
2. Optimize database queries
3. Implement caching strategies
4. Minimize data transfer
5. Optimize payload sizes
6. Use asynchronous processing
7. Regular performance reviews

## Troubleshooting

### High Latency

**Diagnosis**:
```
1. Measure latency at each layer
2. Check geographic distance
3. Review connection establishment time
4. Analyze DNS resolution time
5. Check database query performance
6. Review external API latency
7. Examine application processing time
```

**Solutions**:
```
- Deploy closer to users
- Use CDN
- Implement caching
- Optimize database
- Use connection pooling
- Enable compression
- Upgrade network capacity
```

### Low Throughput

**Diagnosis**:
```
1. Measure bandwidth utilization
2. Check instance network limits
3. Review security group rules
4. Analyze packet loss
5. Check MTU settings
6. Review NAT gateway limits
7. Examine cross-region transfer
```

**Solutions**:
```
- Upgrade instance types
- Use enhanced networking
- Implement compression
- Optimize data transfer patterns
- Use Direct Connect/ExpressRoute
- Enable jumbo frames (intra-VPC)
- Parallel transfers
```

### Connection Issues

**Diagnosis**:
```
1. Check connection count
2. Review timeout settings
3. Analyze connection errors
4. Check load balancer health
5. Review security groups
6. Examine application logs
```

**Solutions**:
```
- Increase connection limits
- Implement connection pooling
- Adjust timeout values
- Scale backend resources
- Fix security group rules
- Optimize application
```

## Conclusion

Network performance optimization requires a holistic approach covering infrastructure design, protocol optimization, caching strategies, and continuous monitoring. Implement best practices, measure regularly, and optimize based on actual performance data.
