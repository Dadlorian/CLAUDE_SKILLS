# Observability Best Practices Reference

## The Three Pillars of Observability

### Metrics
```
Definition: Quantitative measurements at points in time
Characteristics:
  - Numeric values
  - Time-stamped
  - Low cardinality (limited dimensions)
  - Pre-aggregated

Examples:
  - Interface throughput (bytes/sec)
  - CPU utilization (%)
  - Packet loss count
  - Connection count
```

### Logs
```
Definition: Individual event records
Characteristics:
  - Discrete events
  - Rich context and detail
  - Variable cardinality
  - Full request/transaction info

Examples:
  - Device startup messages
  - Interface transitions
  - Configuration changes
  - Error conditions
  - Application transactions
```

### Traces
```
Definition: Request path through distributed system
Characteristics:
  - Distributed request tracking
  - Latency breakdown
  - Dependency mapping
  - Service-to-service visibility

Examples:
  - End-to-end request flow
  - Microservice call chains
  - API gateway → backend service paths
  - Transaction completion status
```

## Instrumentation Strategy

### What to Monitor

#### Critical Systems
```
Priority 1 (Monitor):
  - Internet connectivity
  - Core backbone links
  - Data center uplinks
  - Security appliances
  - DNS servers

Metrics:
  - Availability (99.99%)
  - Latency (<50ms)
  - Packet loss (0%)
  - Error rate (0%)
```

#### Supporting Systems
```
Priority 2 (Monitor):
  - Access network
  - Internal services
  - Backup links
  - Management interfaces

Targets:
  - Availability (99.9%)
  - Latency (<100ms)
  - Throughput trending
  - Error alerting
```

#### Non-Critical Systems
```
Priority 3 (Monitor):
  - Lab equipment
  - Non-production systems
  - Backup infrastructure

Focus:
  - Capacity trending
  - Historical analysis
  - Ad-hoc troubleshooting
```

### Sampling Strategies

#### Full Instrumentation
```
When: Low-volume systems, critical paths
Cost: High (storage and processing)
Benefit: Complete visibility
Use case: Security transactions, payment processing
```

#### Probabilistic Sampling
```
Approach: Sample X% of requests/events
Example: Sample 1 in 100 requests (1%)
Benefit: 100x storage reduction
Tradeoff: Miss rare events
Formula: Storage = (1 / sample_rate) × storage_per_item
```

#### Stratified Sampling
```
Approach: Higher rate for errors, low rate for normal
Benefits:
  - Catch all errors
  - Reduce storage for normal cases
  - Better anomaly detection

Implementation:
  - 100% error sampling
  - 10% normal sampling
  - Adaptive sampling
```

#### Tail Sampling
```
Approach: Sample based on characteristics
Examples:
  - Always sample slow requests (>1000ms)
  - Always sample errors
  - Sample requests with specific headers
  - Sample requests from specific users

Benefit: Focus on interesting cases
Tool: Tail sampling processor in OpenTelemetry
```

## Metric Design

### Metric Naming
```
Format: [namespace]_[subsystem]_[name]_[unit]

Examples:
  network_interface_inbound_bytes
  network_interface_error_count
  network_device_cpu_percent
  network_bgp_neighbor_state
  network_latency_milliseconds
  network_packet_loss_ratio

Principles:
  - Descriptive names
  - Consistent unit suffix
  - Avoid abbreviations
  - Lower_case with underscores
```

### Label/Tag Design

#### High Cardinality (BAD)
```
Metrics with millions of combinations:
  - Customer ID
  - Session ID
  - User ID
  - Request ID
  - Timestamp

Impact:
  - Explosion of unique metric combinations
  - High storage costs
  - Query performance issues
  - Cardinality limits exceeded

Solution: Move to logs or traces
```

#### Appropriate Cardinality (GOOD)
```
Typical cardinality dimensions:
  - Device name/IP (hundreds)
  - Interface name (thousands)
  - Severity level (4-5 values)
  - Service type (10-50 values)
  - Region/site (< 100 values)

Target: 10-1000 combinations per metric
Avoid: >10K combinations per metric
```

### Metric Types

#### Counter
```
Definition: Only increases, never decreases
Use cases:
  - Total bytes sent/received
  - Total packets sent/received
  - Total errors observed
  - Total requests processed

Query: Use rate() function
Example: rate(network_bytes_sent_total[5m])
```

#### Gauge
```
Definition: Can increase or decrease
Use cases:
  - Current interface utilization
  - Current queue depth
  - Current connection count
  - Current memory usage

Query: Direct value or percentage
Example: network_interface_utilization
```

#### Histogram
```
Definition: Observe values into buckets
Use cases:
  - Latency measurements
  - Packet size distribution
  - Response time percentiles

Query: Percentile calculation
Example: histogram_quantile(0.95, latency_seconds_bucket)
```

#### Summary
```
Definition: Similar to histogram, fewer buckets
Use cases:
  - Request duration summaries
  - Response size summaries

Note: Avoid summaries, use histograms instead
```

## Alerting Best Practices

### Alert Severity Levels

#### Critical (Immediate Action Required)
```
Definition: Service is down or severely degraded
Action: Page on-call engineer immediately
Examples:
  - Interface down > 1 minute
  - Packet loss > 10%
  - Device unreachable
  - BGP neighbor down

Response time: 5 minutes
```

#### Warning (Investigate Soon)
```
Definition: Potential problem, needs investigation
Action: Notify team, review in morning
Examples:
  - Link utilization > 80%
  - Error rate > 1%
  - CPU utilization > 90%
  - Memory usage > 85%

Response time: 1 hour
```

#### Info (Awareness)
```
Definition: Informational, expected behavior
Action: Log and track for trending
Examples:
  - Configuration changed
  - Interface brought up/down
  - Service restarted
  - Routine maintenance

Action: Review in daily briefing
```

### Alert Tuning

#### Reducing False Positives
```
1. Increase threshold stability
   - Require N consecutive violations
   - Use moving average instead of instant

2. Context awareness
   - Exclude scheduled maintenance windows
   - Adjust thresholds by time of day

3. Aggregation
   - Alert on pattern, not single event
   - Combine related metrics

4. Dynamic thresholds
   - ML-based anomaly detection
   - Adaptive baselines
```

#### Example Alert Rules
```
Good:
  - Link > 85% for 5 minutes (sustained problem)
  - CPU > 95% for 10 minutes (real congestion)
  - Errors > 100/sec for 2 minutes (pattern)

Bad:
  - Link > 75% once (temporary spike)
  - CPU > 80% instantly (might be transient)
  - Single error packet (noise)
```

## Data Retention Strategy

### Storage Calculation
```
Formula: Daily Volume = (Metrics × Samples/day × Bytes/sample)

Example:
  1000 metrics
  × 12 samples/day (2-hour scrape)
  × 100 bytes average
  = 1.2 MB per day
  × 365 days
  = 438 MB per year

Add 30% overhead: ~570 MB per year
```

### Tiered Retention
```
Hot Storage (Real-time queries):
  Duration: 2 weeks
  Resolution: Full
  Cost: High (~$1000/month per TB)
  Use: Live dashboards, alerting

Warm Storage (Week to month):
  Duration: 3 months
  Resolution: 5-minute aggregates
  Cost: Medium (~$100/month per TB)
  Use: Trending, week-level analysis

Cold Storage (Long-term):
  Duration: 1+ years
  Resolution: 1-hour or 1-day
  Cost: Low (~$10/month per TB)
  Use: Capacity planning, annual trends
```

### Data Aggregation
```
Precision Loss vs Storage Reduction:
  Real-time: Every 15 seconds
  1-hour: Drop to 5-minute averages
  1-day: Drop to 1-hour averages
  1-year: Drop to 1-day aggregates

Trade-off: Query precision vs storage cost
```

## Privacy & Security

### Sensitive Data Handling

#### PII (Personally Identifiable Information)
```
Examples to avoid in metrics:
  - User IDs
  - Session IDs
  - Email addresses
  - Phone numbers
  - Transaction IDs

Solution: Hash or anonymize
  - Use synthetic IDs
  - Hash with salt
  - Remove from logs
```

#### Credential/Secret Handling
```
Never log:
  - Passwords
  - API keys
  - Certificates
  - Authentication tokens
  - Encryption keys

Masking strategies:
  - Strip passwords before logging
  - Replace with [REDACTED]
  - Log only presence, not values
```

### Access Control

#### Role-Based Access (RBAC)
```
Admin: Full access to all data
Operator: Read-only to operational dashboards
Manager: Aggregated business metrics only
Developer: Development environment only
```

#### Data Segregation
```
By environment:
  - Production (restricted)
  - Staging (more open)
  - Development (fully open)

By team:
  - Network team: All network metrics
  - Security: Security-related only
  - Finance: Billing/capacity metrics
```

## Performance Optimization

### Query Optimization
```
Inefficient:
  - High cardinality label combinations
  - Queries across months of data
  - Complex nested expressions

Optimized:
  - Pre-aggregated recording rules
  - Limited time ranges
  - Simplified queries
```

### Cardinality Management
```
Monitor:
  prometheus_tsdb_symbol_table_size_bytes

Optimize:
  1. Identify high-cardinality metrics
     topk(20, count({__name__=~".+"}))

  2. Drop unnecessary labels
     metric_relabel_configs

  3. Limit dimensions
     max 10 labels per metric

  4. Use recording rules
     Pre-compute high-cost queries
```

## Observability at Scale

### Multi-Region Strategy
```
Federated Prometheus:
  - Local Prometheus per region
  - Central aggregation point
  - Query federation for global view

Advantages:
  - Reduced latency
  - Data sovereignty
  - Failure isolation

Challenges:
  - Synchronization
  - Deduplication
  - Complexity
```

### High Availability
```
Prometheus HA:
  - Multiple Prometheus servers
  - Same scrape configuration
  - Deduplicate via Cortex/Thanos
  - Remote storage backend

Remote Storage:
  - S3/GCS for object storage
  - Time series database (Influx, Cortex)
  - Elasticsearch for logs
```

## Implementation Roadmap

### Phase 1: Foundation (Month 1)
```
1. Deploy metrics collection (Prometheus + exporters)
2. Create basic dashboards
3. Define critical metrics
4. Set up alerting for critical paths
5. Establish baseline performance
```

### Phase 2: Enrichment (Months 2-3)
```
1. Add log aggregation (ELK/Loki)
2. Create operational runbooks
3. Implement alert tuning
4. Add streaming telemetry
5. Expand metric coverage
```

### Phase 3: Optimization (Months 4-6)
```
1. Implement data retention tiers
2. Add ML-based anomaly detection
3. Build trend analysis
4. Optimize cardinality
5. Scale to multi-region (if needed)
```

### Phase 4: Intelligence (Months 6+)
```
1. Predictive alerting
2. Automated remediation
3. Capacity planning AI
4. Business impact correlation
5. AIOps integration
```

## Implementation Checklist

- [ ] Define observability requirements
- [ ] Classify systems by criticality
- [ ] Design metric namespace
- [ ] Plan label strategy
- [ ] Establish retention policy
- [ ] Configure data aggregation
- [ ] Implement sampling strategy
- [ ] Set up access controls
- [ ] Create data privacy procedures
- [ ] Design alert rules
- [ ] Document escalation procedures
- [ ] Plan for scale and growth

---

**Reference Type**: Architecture & Best Practices
**Primary Use**: Observability system design
**Focus**: Enterprise networks and systems
**Last Updated**: 2025-11-19
